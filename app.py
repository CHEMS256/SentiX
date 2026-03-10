from flask import Flask, render_template_string, request, jsonify, send_file
import requests
import os
import pandas as pd
import re
from pathlib import Path
import uuid
import tempfile
from werkzeug.utils import secure_filename
from langdetect import detect
import warnings

warnings.filterwarnings("ignore")

app = Flask(__name__)
BASEDIR = Path(__file__).resolve().parent

if os.environ.get("VERCEL"):
    temp_dir = Path(tempfile.gettempdir())
    app.config["UPLOAD_FOLDER"] = temp_dir / "uploads"
    app.config["RESULT_FOLDER"] = temp_dir / "resultats_analyse"
else:
    app.config["UPLOAD_FOLDER"] = BASEDIR / "uploads"
    app.config["RESULT_FOLDER"] = BASEDIR / "resultats_analyse"

app.config["MAX_CONTENT_LENGTH"] = 16 * 1024 * 1024

os.makedirs(app.config["UPLOAD_FOLDER"], exist_ok=True)
os.makedirs(app.config["RESULT_FOLDER"], exist_ok=True)


class APIIntelligente:
    def detecter_langue(self, texte):
        if not texte or pd.isna(texte):
            return "fr"

        texte = str(texte).lower()

        if re.search(r"[\u0600-\u06FF]", texte):
            darija_markers = [
                "زوين", "خير", "بزاف", "مزيان", "خايب", "نكرة",
                "حشومة", "عجبني", "ماعجبنيش", "غالي", "مخرب"
            ]
            if any(w in texte for w in darija_markers):
                return "darija"
            return "ar"

        try:
            lang = detect(texte)
            return lang if lang in ["fr", "en"] else "fr"
        except:
            return "fr"

    def analyser_expression_contextuelle(self, texte, langue):
        if not texte:
            return None

        texte = str(texte).lower()

        positif = {
            "fr": [
                "bon", "excellent", "super", "génial", "parfait", "top",
                "efficace", "rapide", "satisfait", "recommande", "agréable", "merci"
            ],
            "en": [
                "good", "great", "excellent", "perfect", "amazing",
                "love", "fast", "nice"
            ],
            "ar": [
                "جيد", "ممتاز", "رائع", "مثالي", "سريع"
            ],
            "darija": [
                "زوين", "خير", "كويس", "باركا", "حلو", "ممتاز",
                "مزيان", "صافي", "عجبني", "تبارك الله", "نتا",
                "بزاف زوين", "راه زوين"
            ]
        }

        negatif = {
            "fr": [
                "mauvais", "nul", "horrible", "lent", "bug", "problème",
                "déçu", "arnaque", "cher", "éviter", "pire"
            ],
            "en": [
                "bad", "terrible", "worst", "slow", "fail",
                "disappointed", "scam"
            ],
            "ar": [
                "سيء", "رديء", "فشل", "بطيء"
            ],
            "darija": [
                "خايب", "مشي", "ماعندوش", "سيء", "رديء", "نكرة",
                "حشومة", "مخرب", "خسارة", "غالي", "ما عجبنيش",
                "راه خايب", "عيب عليكم", "فاشل", "وصل مخرب"
            ]
        }

        score = 0
        pos_words = positif.get(langue, [])
        neg_words = negatif.get(langue, [])

        for w in pos_words:
            if w in texte:
                score += 1

        for w in neg_words:
            if w in texte:
                score -= 1

        if score > 0:
            return "positif"
        elif score < 0:
            return "negatif"
        return None


class AnalyseurSentimentsNLPCloud:
    def __init__(self):
        self.api = APIIntelligente()
        self.url = "https://api.nlpcloud.com/v1/french/sentiment"
        self.api_key = os.environ.get("NLPCLOUD_API_KEY", "ab274e2f717991b3eb75166a1fe9b175b21cf31d")

    def analyser_texte(self, texte):
        texte = str(texte).strip()

        if len(texte) < 3:
            return "neutre"

        if self.api_key:
            try:
                headers = {"Authorization": f"Token {self.api_key}"}
                data = {"text": texte[:1000]}
                resp = requests.post(self.url, headers=headers, json=data, timeout=8)

                if resp.status_code == 200:
                    result = resp.json()
                    score = result.get("score_tag", "NEU")
                    return {
                        "P+": "positif",
                        "P": "positif",
                        "N+": "negatif",
                        "N": "negatif",
                        "NEU": "neutre"
                    }.get(score, "neutre")
            except:
                pass

        langue = self.api.detecter_langue(texte)
        return self.api.analyser_expression_contextuelle(texte, langue) or "neutre"

    def analyser_batch(self, df, col):
        df = df.copy()

        if col not in df.columns:
            return pd.DataFrame()

        df["texte"] = df[col].fillna("").astype(str)
        df = df[df["texte"].str.len() > 2].reset_index(drop=True)

        if df.empty:
            return pd.DataFrame()

        df["langue"] = df["texte"].apply(self.api.detecter_langue)
        df["sentiment_final"] = df["texte"].apply(self.analyser_texte)
        df["ligne_excel"] = df.index + 2

        return df.rename(columns={col: "avis"})[
            ["avis", "langue", "sentiment_final", "ligne_excel"]
        ]


class GestionnaireExcel:
    def __init__(self):
        self.analyseur = AnalyseurSentimentsNLPCloud()

    def detecter_colonne_avis(self, df):
        for c in df.columns:
            if any(word in str(c).lower() for word in ["avis", "comment", "text", "review"]):
                return c

        for c in df.columns:
            if df[c].dtype == "object":
                return c

        return df.columns[0]

    def analyser_fichier_excel(self, path, output_dir):
        output_dir = Path(output_dir)

        try:
            if path.endswith((".xlsx", ".xls")):
                df = pd.read_excel(path)
            else:
                df = pd.read_csv(path)

            if df.empty:
                return None, None

            col = self.detecter_colonne_avis(df)
            df_res = self.analyseur.analyser_batch(df, col)

            if df_res.empty:
                return None, None

            out_path = output_dir / f"analyse_{pd.Timestamp.now().strftime('%Y%m%d_%H%M%S')}.xlsx"
            df_res.to_excel(out_path, index=False)

            return df_res, out_path

        except Exception as e:
            print(f"Erreur: {e}")
            raise


gestionnaire = GestionnaireExcel()
print("Modèle prêt !")


@app.route("/")
def home():
    chemin = BASEDIR / "index.html"
    try:
        with open(chemin, "r", encoding="utf-8") as f:
            return render_template_string(f.read())
    except FileNotFoundError:
        return "<h1>Fichier index.html manquant</h1>", 404


@app.route("/upload", methods=["POST"])
def upload_file():
    if "file" not in request.files:
        return jsonify({"error": "Aucun fichier"}), 400

    file = request.files["file"]

    if file.filename == "":
        return jsonify({"error": "Fichier vide"}), 400

    filename = secure_filename(file.filename)
    unique_filename = f"{uuid.uuid4()}_{filename}"
    filepath = os.path.join(app.config["UPLOAD_FOLDER"], unique_filename)
    file.save(filepath)

    try:
        df_result, result_path = gestionnaire.analyser_fichier_excel(
            filepath, app.config["RESULT_FOLDER"]
        )

        if os.path.exists(filepath):
            os.remove(filepath)

        if df_result is None or df_result.empty:
            return jsonify({"error": "Aucun avis valide"}), 500

        total = len(df_result)
        sentiments = df_result['sentiment_final'].value_counts().to_dict()
        langues = df_result['langue'].value_counts().to_dict()
        preview = df_result[['avis', 'langue', 'sentiment_final']].to_dict(orient='records')

        return jsonify({
            "status": "success",
            "total": total,
            "distribution": sentiments,
            "langues": langues,
            "preview": preview,
            "download_url": f"/download/{result_path.name}"
        })

    except Exception as e:
        if os.path.exists(filepath):
            os.remove(filepath)
        return jsonify({"error": str(e)}), 500


@app.route("/download/<filename>")
def download_file(filename):
    try:
        return send_file(
            os.path.join(app.config["RESULT_FOLDER"], filename),
            as_attachment=True
        )
    except:
        return jsonify({"error": "Fichier introuvable"}), 404


if __name__ == "__main__":
    port = int(os.environ.get("PORT", 5000))
    app.run(host="0.0.0.0", port=port)

