from sqlalchemy import Column, Integer, String, Boolean, DateTime, ForeignKey, Text
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func
from .database import Base

class User(Base):
    __tablename__ = "Users"

    UserID = Column(Integer, primary_key=True, autoincrement=True)
    Email = Column(String(255), unique=True, nullable=False)
    HashedPassword = Column(String(255), nullable=False)
    Role = Column(String(50), nullable=False) # 'student', 'professor', 'admin'
    IsActive = Column(Boolean, server_default='1')
    UserIdentifier = Column(String(100), nullable=True) # Full Name
    CreatedAt = Column(DateTime, server_default=func.now())

    # Relationships
    student_profile = relationship("Student", back_populates="user", uselist=False, cascade="all, delete-orphan")


class Student(Base):
    __tablename__ = "Students"

    StudentID = Column(Integer, primary_key=True, autoincrement=True)
    UserIdentifier = Column(String(100), unique=True, nullable=False)
    CreatedAt = Column(DateTime, server_default=func.now())
    UserID = Column(Integer, ForeignKey("Users.UserID"), nullable=True)

    # Relationships
    user = relationship("User", back_populates="student_profile")
    submissions = relationship("Submission", back_populates="student", cascade="all, delete-orphan")


class Submission(Base):
    __tablename__ = "Submissions"

    SessionID = Column(String(255), primary_key=True)
    StudentID = Column(Integer, ForeignKey("Students.StudentID"), nullable=False)
    Subject_Submission = Column(String(100), nullable=False)
    DocumentType = Column(String(50), nullable=False)
    SubmissionText = Column(Text, nullable=True) # NVARCHAR(MAX) equivalent
    SubmissionDate = Column(DateTime, server_default=func.now())

    # Relationships
    student = relationship("Student", back_populates="submissions")
    progress_tracking = relationship("ProgressTracking", back_populates="submission", cascade="all, delete-orphan")
    correction_result = relationship("CorrectionResult", back_populates="submission", uselist=False, cascade="all, delete-orphan")


class ProgressTracking(Base):
    __tablename__ = "ProgressTracking"

    DifficultyID = Column(Integer, primary_key=True, autoincrement=True)
    SessionID = Column(String(255), ForeignKey("Submissions.SessionID"), nullable=False)
    DifficultyText = Column(Text, nullable=False)
    Status = Column(String(20), server_default='Active')

    # Relationships
    submission = relationship("Submission", back_populates="progress_tracking")


class CorrectionResult(Base):
    __tablename__ = "CorrectionResults"

    SessionID = Column(String(255), ForeignKey("Submissions.SessionID"), primary_key=True)
    TotalScore = Column(Integer, nullable=False)
    Passed = Column(Boolean, nullable=False)
    GradedAt = Column(DateTime, server_default=func.now())

    # Relationships
    submission = relationship("Submission", back_populates="correction_result")
    phase_evaluations = relationship("PhaseEvaluation", back_populates="correction_result", cascade="all, delete-orphan")
    correction_errors = relationship("CorrectionError", back_populates="correction_result", cascade="all, delete-orphan")
    feedback_report = relationship("FeedbackReport", back_populates="correction_result", uselist=False, cascade="all, delete-orphan")


class PhaseEvaluation(Base):
    __tablename__ = "PhaseEvaluations"

    EvaluationID = Column(Integer, primary_key=True, autoincrement=True)
    SessionID = Column(String(255), ForeignKey("CorrectionResults.SessionID"), nullable=False)
    PhaseName = Column(String(100), nullable=False)
    Score = Column(Integer, nullable=False)
    Justification = Column(Text, nullable=False)

    # Relationships
    correction_result = relationship("CorrectionResult", back_populates="phase_evaluations")


class CorrectionError(Base):
    __tablename__ = "CorrectionErrors"

    ErrorID = Column(Integer, primary_key=True, autoincrement=True)
    SessionID = Column(String(255), ForeignKey("CorrectionResults.SessionID"), nullable=False)
    ErrorText = Column(Text, nullable=False)

    # Relationships
    correction_result = relationship("CorrectionResult", back_populates="correction_errors")


class FeedbackReport(Base):
    __tablename__ = "FeedbackReports"

    ReportID = Column(Integer, primary_key=True, autoincrement=True)
    SessionID = Column(String(255), ForeignKey("CorrectionResults.SessionID"), nullable=False)
    ProfessorSummary = Column(Text, nullable=True)
    PedagogicalWarning = Column(Text, nullable=True)
    StudentDraftReport = Column(Text, nullable=True)
    ApprovalStatus = Column(String(50), server_default='Pending')
    GeneratedAt = Column(DateTime, nullable=True)
    ApprovedAt = Column(DateTime, nullable=True)
    ProfessorObservations = Column(Text, nullable=True)

    # Relationships
    correction_result = relationship("CorrectionResult", back_populates="feedback_report")