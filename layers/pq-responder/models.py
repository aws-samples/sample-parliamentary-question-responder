"""
This module provides data models for handling parliamentary publications and questions.
It includes classes for managing publications, documents, and parliamentary questions
from both the House of Commons and House of Lords.
"""

from typing import Dict, List, Optional
from datetime import date
from enum import Enum
from dateutil import parser
from pydantic import BaseModel, computed_field
from aws_lambda_powertools import Logger

logging = Logger()


class House(Enum):
    """Enumeration of parliamentary houses."""
    COMMONS = "commons"
    LORDS = "lords"


class PublicationFile(BaseModel):
    """Model representing a publication file."""
    filename: str

    @classmethod
    def from_dict(cls, data: Dict[str, str]) -> "PublicationFile":
        """Create a PublicationFile instance from a dictionary.
        
        Args:
            data: Dictionary containing filename
            
        Returns:
            PublicationFile instance
        """
        return cls(filename=data["filename"])


class PublicationDocument(BaseModel):
    """Model representing a document within a publication."""
    id: int
    publication_id: Optional[int] = None
    files: Optional[List[PublicationFile]] = []

    @computed_field
    @property
    def api_uri_path(self) -> str:
        """Generate API URI path for the document.
        
        Returns:
            String containing the API URI path
        """
        return f"Publications/{self.publication_id}/Document/{self.id}/OriginalFormat"

    @computed_field
    @property
    def web_uri_path(self) -> str:
        """Generate web URI path for the document.
        
        Returns:
            String containing the web URI path
        """
        return f"publications/{self.publication_id}/documents/{self.id}/default"

    def append(self, file: PublicationFile):
        """Add a file to the document.
        
        Args:
            file: PublicationFile to append
        """
        self.files.append(file)

    @classmethod
    def from_dict(cls, data: Dict[str, any]) -> "PublicationDocument":
        """Create a PublicationDocument instance from a dictionary.
        
        Args:
            data: Dictionary containing document data
            
        Returns:
            PublicationDocument instance
        """
        files = [PublicationFile.from_dict(f) for f in data.get("files", [])]
        return cls(id=data["id"], publication_id=data["publication_id"], files=files)


class Publication(BaseModel):
    """Model representing a parliamentary publication."""
    committee_id: int
    id: int
    description: str
    documents: Optional[List[PublicationDocument]] = []

    def append(self, document: PublicationDocument):
        """Add a document to the publication.
        
        Args:
            document: PublicationDocument to append
        """
        document.publication_id = self.id
        self.documents.append(document)

    @classmethod
    def from_dict(cls, data: Dict[str, any]) -> "Publication":
        """Create a Publication instance from a dictionary.
        
        Args:
            data: Dictionary containing publication data
            
        Returns:
            Publication instance
        """
        documents = [
            PublicationDocument.from_dict(d) for d in data.get("documents", [])
        ]
        return cls(
            committee_id=data["committee_id"],
            id=data["id"],
            description=data["description"],
            documents=documents,
        )


class Publications(BaseModel):
    """Collection of parliamentary publications."""
    committee_api_base_uri: str
    publications: Optional[List[Publication]] = []

    def append(self, publication: Publication):
        """Add a publication to the collection.
        
        Args:
            publication: Publication to append
        """
        self.publications.append(publication)


class Question(BaseModel):
    """Model representing a parliamentary question."""
    id: int
    question: str
    answer: Optional[str] = ""
    date_tabled: date
    house: House

    @property
    def complete_question(self):
        """Check if the question text is complete.
        
        Returns:
            Boolean indicating if question is complete
        """
        return not self.question.endswith("...")

    @property
    def complete_answer(self):
        """Check if the answer text is complete.
        
        Returns:
            Boolean indicating if answer is complete
        """
        if self.answer is None:
            return True
        return not self.answer.endswith("...")

    def _validate_date(self, value):
        """Validate and parse a date value.
        
        Args:
            value: Date string or date object to validate
            
        Returns:
            Validated date object
            
        Raises:
            ValueError: If date is invalid
        """
        if isinstance(value, str):
            try:
                return date.fromisoformat(value[:10])
            except ValueError as e:
                logging.error("Invalid date_tabled value: %s", e)
        elif isinstance(value, date):
            return value
        else:
            raise ValueError(f"Invalid date_tabled value: {value}")

    @classmethod
    def from_dict(cls, data: Dict[str, str]) -> "Question":
        """Create a Question instance from a dictionary.
        
        Args:
            data: Dictionary containing question data
            
        Returns:
            Question instance
        """
        return cls(
            id=int(data["id"]),
            question=data["question"],
            answer=data["answer"],
            date_tabled=parser.parse(data["date_tabled"][:10]),
            house=House(data["house"]),
        )

    def to_dict(self) -> Dict[str, str]:
        """Convert question to dictionary format.
        
        Returns:
            Dictionary representation of the question
        """
        return {
            "id": self.id,
            "question": self.question,
            "answer": self.answer,
            "date_tabled": self.date_tabled.isoformat(),
            "house": self.house.value,
        }


class Questions(BaseModel):
    """Collection of parliamentary questions."""

    questions: List[Question] = []

    def __iter__(self):
        """Iterator for questions collection."""
        return iter(self.questions)

    def __len__(self):
        """Get number of questions in collection."""
        return len(self.questions)

    def add(self, question: Question):
        """Add a question to the collection.
        
        Args:
            question: Question to append
        """
        self.questions.append(question)

    @classmethod
    def from_dict_list(cls, data: List[Dict[str, str]]) -> "Questions":
        """Create a Questions instance from a list of dictionaries.
        
        Args:
            data: List of dictionaries containing question data
            
        Returns:
            Questions instance
        """
        questions = [Question.from_dict(q) for q in data]
        return cls(questions=questions)

    def to_dict_list(self) -> List[Dict[str, str]]:
        """Convert questions collection to list of dictionaries.
        
        Returns:
            List of dictionary representations of questions
        """
        return [q.to_dict() for q in self.questions]
