"""
This module provides API clients for interacting with the Parliament API services.
It includes clients for accessing committee information, publications, and questions.
Each client handles request retries and data validation.
"""

from datetime import date, time, datetime
from base64 import b64decode
from urllib.parse import urlparse
from enum import Enum
from dateutil import parser
from urllib3.util import Retry


import requests
import requests.adapters
import requests.exceptions
import validators

from aws_lambda_powertools import Logger, Tracer, Metrics

from models import (
    Publications,
    Publication,
    PublicationDocument,
    PublicationFile,
    Question,
    Questions,
    House,
)

logger = Logger()
tracer = Tracer()
metrics = Metrics()

TAKE = 1000


def validate_base_uri(base_uri):
    """
    Validates that the provided base URI meets the required format.

    Args:
        base_uri (str): The base URI to validate

    Returns:
        bool: True if validation passes

    Raises:
        ValueError: If base_uri is empty, not a valid URL, contains fragments/parameters,
                   doesn't end with '/', or isn't http/https
    """
    if not base_uri:
        raise ValueError("base_uri is required")

    if not validators.url(base_uri):
        raise ValueError("base_uri is not a valid URL")

    parsed_base_uri = urlparse(base_uri)

    if parsed_base_uri.fragment:
        raise ValueError("base_uri must not contain a fragment")

    if parsed_base_uri.query != "":
        raise ValueError("base_uri must not contain parameters")

    if parsed_base_uri.path[-1:] != "/":
        raise ValueError('base_uri must end with "/"')

    if parsed_base_uri.scheme not in ["http", "https"]:
        raise ValueError("base_uri must be http or https")

    return True


def validate_start_end_dates(start_date_tabled: date, end_date_tabled: date):
    """
    Validates that the provided date range is valid.

    Args:
        start_date_tabled (date): Start date of the range
        end_date_tabled (date): End date of the range

    Raises:
        ValueError: If dates are not date objects, start date is after end date,
                   or dates are in the future
    """
    if not isinstance(start_date_tabled, date) or not isinstance(end_date_tabled, date):
        raise ValueError(
            "start_date_tabled and end_date_tabled must be datetime.date objects"
        )

    if start_date_tabled > end_date_tabled:
        raise ValueError("start_date_tabled must be before end_date_tabled")

    if start_date_tabled > date.today() or end_date_tabled > date.today():
        raise ValueError("start_date_tabled and end_date_tabled must be in the past")


# pylint: disable=too-few-public-methods
class ParliamentCommitteesAPIClient:
    """Client for accessing Parliament Committee API endpoints."""

    def __init__(self, base_uri: str):
        """
        Initialize the client with base URI and configure session.

        Args:
            base_uri (str): Base URI for the API

        Raises:
            ValueError: If base_uri is invalid
        """
        try:
            validate_base_uri(base_uri)

        except ValueError as e:
            logger.warning("Invalid base uri %s", e)
            raise e

        self.base_uri = base_uri
        self.session = requests.Session()

        retries = Retry(total=3, backoff_factor=0.4)

        self.session.mount(
            "base_uri", requests.adapters.HTTPAdapter(max_retries=retries)
        )

    def get_sub_committees(self, parent_committee_id: int) -> list:
        """
        Get list of sub-committees for a parent committee.

        Args:
            parent_committee_id (int): ID of the parent committee

        Returns:
            list: List of sub-committee dictionaries with id and name
        """
        url = f"{self.base_uri}committees/{parent_committee_id}"

        try:
            response = self.session.get(url)
            response.raise_for_status()
            committee_json = response.json()

            sub_committees = [
                {"id": sub_committee["id"], "name": sub_committee["name"]}
                for sub_committee in committee_json["subCommittees"]
            ]

            return sub_committees
        finally:
            response.close()


class ParliamentPublicationsAPIClient:
    """Client for accessing Parliament Publications API endpoints."""

    def __init__(self, base_uri: str):
        """
        Initialize the client with base URI and configure session.

        Args:
            base_uri (str): Base URI for the API

        Raises:
            ValueError: If base_uri is invalid
        """
        try:
            validate_base_uri(base_uri)

        except ValueError as e:
            logger.warning("Invalid base uri %s", e)
            raise e

        self.base_uri = base_uri
        self.session = requests.Session()

        retries = Retry(total=3, backoff_factor=0.4)

        self.session.mount(
            "base_uri", requests.adapters.HTTPAdapter(max_retries=retries)
        )

    def get_publication_file(self, publication: Publication) -> dict:
        """
        Get file data for a publication.

        Args:
            publication (Publication): Publication object containing document info

        Returns:
            dict: Dictionary containing base_uri and decoded file data

        Raises:
            requests.exceptions.ConnectionError: If connection fails
            requests.exceptions.Timeout: If request times out
            requests.exceptions.HTTPError: If HTTP error occurs
            requests.exceptions.RequestException: For other request errors
            Exception: For unexpected errors
        """
        url = f"{self.base_uri}{publication.documents[0].api_uri_path}"

        try:
            logger.debug("Fetching %s", url)
            response = self.session.get(url)
            response.raise_for_status()
            logger.debug("Status Code: %s for %s", response.status_code, url)

            data = b64decode(response.json()["data"])
            file = {"base_uri": self.base_uri, "data": data}
            return file
        except requests.exceptions.ConnectionError as e:
            logger.error("Connection failed: %s", str(e))
            raise

        except requests.exceptions.Timeout as e:
            logger.error("Request timed out: %s", str(e))
            raise

        except requests.exceptions.HTTPError as e:
            logger.error("HTTP error occurred: %s - %s", e.response.status_code, str(e))
            raise

        except requests.exceptions.RequestException as e:
            # Catches all requests exceptions not caught above
            logger.error("Request failed: %s", str(e))
            raise

        except Exception as e:
            # Catches any other unexpected exceptions
            logger.error("Unexpected error: %s", str(e))
            raise

        finally:
            response.close()

    # pylint: disable=too-many-locals
    def get_committee_publications_list(
        self, committee_id: int, start_date: date, end_date: date
    ) -> Publications:
        """
        Get list of publications for a committee within a date range.

        Args:
            committee_id (int): ID of the committee
            start_date (date): Start date for publication search
            end_date (date): End date for publication search

        Returns:
            Publications: Object containing list of publications with documents and files

        Raises:
            requests.exceptions.RequestException: For request errors
        """
        validate_start_end_dates(start_date, end_date)

        skip = 0
        publications_obj = Publications(committee_api_base_uri=self.base_uri)

        start_date_iso = datetime.combine(start_date, time(0, 0, 0)).isoformat()
        end_date_iso = datetime.combine(end_date, time(0, 0, 0)).isoformat()

        try:
            while True:
                url = f"{self.base_uri}publications/?CommitteeId={committee_id}&StartDate={start_date_iso}&EndDate={end_date_iso}&skip={skip}&take={TAKE}"  # pylint: disable=line-too-long
                response = self.session.get(url)
                response.raise_for_status()
                publications_json = response.json()

                total_results = publications_json["totalResults"]
                skip += TAKE

                for publication in publications_json["items"]:
                    publication_obj = Publication(
                        id=publication["id"],
                        description=publication["description"],
                        committee_id=publication["committee"]["id"],
                    )

                    for document in publication["documents"]:
                        document_obj = PublicationDocument(
                            id=document["documentId"],
                        )
                        for file in document["files"]:
                            file_obj = PublicationFile(filename=file["fileName"])
                            document_obj.append(file_obj)
                        publication_obj.append(document_obj)
                    publications_obj.append(publication_obj)

                if skip >= total_results:
                    break

            return publications_obj
        except requests.exceptions.RequestException as e:
            logger.error(f"HTTP error occurred: {e}")
            raise
        finally:
            response.close()


class DateType(str, Enum):
    """
    Enum representing the type of date to filter questions by.

    Values:
        TABLED: Filter by the date the question was tabled
        ANSWERED: Filter by the date the question was answered
    """

    TABLED = "tabled"
    ANSWERED = "answered"


class ParliamentQuestionsAPIClient:
    """Client for accessing Parliament Questions API endpoints."""

    def __init__(self, base_uri: str):
        """
        Initialize the client with base URI and configure session.

        Args:
            base_uri (str): Base URI for the API

        Raises:
            ValueError: If base_uri is invalid
        """
        try:
            validate_base_uri(base_uri)

        except ValueError as e:
            logger.warning("Invalid base uri %s", e)
            raise e

        self.base_uri = base_uri
        self.session = requests.Session()

        retries = Retry(total=3, backoff_factor=0.4)

        self.session.mount(
            "base_uri", requests.adapters.HTTPAdapter(max_retries=retries)
        )

    def get_question_by_id(self, question_id: int) -> Question:
        """
        Get a specific question by its ID.

        Args:
            question_id (int): ID of the question to retrieve

        Returns:
            Question: Question object containing ID, house, date tabled, question text and answer text
        """
        url = f"{self.base_uri}questions/{question_id}"
        try:
            response = self.session.get(url)
            response.raise_for_status()
            question_json = response.json()

            return Question(
                id=question_json["value"]["id"],
                house=question_json["value"]["house"].lower(),
                date_tabled=parser.parse(question_json["value"]["dateTabled"]),
                question=question_json["value"]["questionText"],
                answer=question_json["value"]["answerText"],
            )
        finally:
            response.close()

    def get_full_question(self, question: Question) -> Question:
        """
        Get complete question and answer if not already present.

        Args:
            question (Question): Question object to complete

        Returns:
            Question: Complete question object with full question and answer text
        """
        if question.complete_question and question.complete_answer:
            return question
        logger.info("Retrieving full question and answer from API")
        metrics.add_metric(name="QuestionAPIRequest", unit="Count", value=1)
        full_question = self.get_question_by_id(question.id)
        return full_question

    def get_questions_by_date(
        self, date_type: DateType, start_date: date, end_date: date
    ):
        """
        Get all questions tabled or answered between two dates.

        Args:
            date_type (DateType): Type of date to filter by (TABLED or ANSWERED)
            start_date (date): Start date for question search
            end_date (date): End date for question search

        Returns:
            Questions: Object containing list of questions

        Raises:
            ValueError: If date_type is invalid
            requests.exceptions.HTTPError: If HTTP error occurs
            requests.exceptions.RequestException: For other request errors
        """
        validate_start_end_dates(start_date, end_date)

        skip = 0
        questions = Questions()

        try:
            while True:
                if date_type == DateType.TABLED:
                    url = f"{self.base_uri}questions?tabledWhenFrom={start_date}&tabledWhenTo={end_date}&skip={skip}&take={TAKE}"
                elif date_type == DateType.ANSWERED:
                    url = f"{self.base_uri}questions?answeredWhenFrom={start_date}&answeredWhenTo={end_date}&skip={skip}&take={TAKE}"
                else:
                    raise ValueError(f"Invalid date_type: {date_type}")

                # amazonq-ignore-next-line as this is caught by the finally block
                response = self.session.get(url)
                response.raise_for_status()

                question_data = response.json()

                total_results = question_data["totalResults"]
                skip += TAKE

                for api_question in question_data["results"]:
                    question = Question(
                        id=api_question["value"]["id"],
                        house=House(api_question["value"]["house"].lower()),
                        date_tabled=parser.parse(
                            api_question["value"]["dateTabled"][:10]
                        ),
                        question=api_question["value"]["questionText"],
                        answer=api_question["value"]["answerText"],
                    )
                    questions.add(question)
                if total_results <= skip:
                    break

            return questions

        except requests.exceptions.HTTPError as e:
            logger.error(f"HTTP error occurred: {e}")
            raise e
        except requests.exceptions.RequestException as e:
            logger.error(f"Request failed: {e}")
            raise e
        finally:
            self.session.close()
