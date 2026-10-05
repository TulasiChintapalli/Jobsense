import json
from datetime import datetime
from ..extensions import db

LISTS = ["technical_skills","soft_skills","education","experience","responsibilities","keywords","missing_skills","recommended_skills"]

class Analysis(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey("user.id"), nullable=False, index=True)
    title = db.Column(db.String(255))
    job_title = db.Column(db.String(255))
    company_name = db.Column(db.String(255))
    original_text = db.Column(db.Text)
    file_name = db.Column(db.String(255))
    overall_score = db.Column(db.Integer)
    ml_prediction = db.Column(db.String(120))
    ml_confidence = db.Column(db.Float)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    result = db.relationship("AnalysisResult", uselist=False, backref="analysis", cascade="all, delete-orphan")
    def to_dict(self, full=False):
        d = dict(id=self.id, title=self.title, job_title=self.job_title, company_name=self.company_name,
                 file_name=self.file_name, overall_score=self.overall_score, ml_prediction=self.ml_prediction,
                 ml_confidence=self.ml_confidence, created_at=self.created_at.isoformat(), ai_available=self.result is not None)
        if full:
            d["original_text"] = self.original_text
            d["result"] = self.result.to_dict() if self.result else None
        return d

class AnalysisResult(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    analysis_id = db.Column(db.Integer, db.ForeignKey("analysis.id"), nullable=False)
    summary = db.Column(db.Text)
    technical_skills = db.Column(db.Text, default="[]")
    soft_skills = db.Column(db.Text, default="[]")
    education = db.Column(db.Text, default="[]")
    experience = db.Column(db.Text, default="[]")
    responsibilities = db.Column(db.Text, default="[]")
    keywords = db.Column(db.Text, default="[]")
    missing_skills = db.Column(db.Text, default="[]")
    recommended_skills = db.Column(db.Text, default="[]")
    def to_dict(self):
        d = {"summary": self.summary}
        for k in LISTS: d[k] = json.loads(getattr(self, k) or "[]")
        return d
