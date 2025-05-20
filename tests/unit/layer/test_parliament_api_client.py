from datetime import date, timedelta

from parliament_api_client import (
    DateType,
    ParliamentQuestionsAPIClient,
    ParliamentCommitteesAPIClient,
    ParliamentPublicationsAPIClient,
)
from mock_data.mock_committee_education import MockEducationCommittee
from mock_data.mock_publication_list import MockPublicationList
from mock_data.mock_api_questions import MockAPIQuestions

from unittest.mock import Mock, MagicMock, patch

import pytest
import requests
import os
import sys

sys.path.append(os.path.join(os.getcwd(), "layers", "pq-responder"))


START_DATE = date(2024, 1, 1)
END_DATE = date(2024, 1, 7)
DATE_TYPE = DateType.ANSWERED

class TestParliamentCommitteesApiClient:
    def test_init_creates_session_with_base_uri(
        self, mock_parliament_committees_api_uri
    ):
        """
        Test that __init__ correctly initializes ParliamentAPIClient with base_uri and creates a requests.Session
        """
        client = ParliamentCommitteesAPIClient(mock_parliament_committees_api_uri)

        assert client.base_uri == mock_parliament_committees_api_uri
        assert isinstance(client.session, requests.Session)

    def test_init_session_creation_failure(
        self, monkeypatch, mock_parliament_committees_api_uri
    ):
        """
        Test initialization when session creation fails.
        """

        def mock_session(*args, **kwargs):
            raise requests.exceptions.RequestException("Failed to create session")

        monkeypatch.setattr(requests, "Session", mock_session)
        with pytest.raises(requests.exceptions.RequestException):
            ParliamentCommitteesAPIClient(mock_parliament_committees_api_uri)

    def test_init_with_empty_base_uri(self):
        """
        Test initialization with an empty base_uri.
        """
        with pytest.raises(ValueError):
            ParliamentCommitteesAPIClient("")

    def test_init_with_invalid_uri(self):
        """
        Test initialization with an invalid URI.
        """
        with pytest.raises(ValueError):
            ParliamentCommitteesAPIClient("not_a_valid_uri")

    def test_init_with_fragment(self, mock_parliament_committees_api_uri):
        """
        Test initialization with a URL fragment in the base_uri.
        """
        with pytest.raises(ValueError):
            ParliamentCommitteesAPIClient(
                f"{mock_parliament_committees_api_uri}#fragment"
            )

    def test_init_with_non_http_protocol(self):
        """
        Test initialization with a non-HTTP protocol.
        """
        with pytest.raises(ValueError):
            ParliamentCommitteesAPIClient("ftp://example.com")

    def test_init_with_query_parameters(self, mock_parliament_committees_api_uri):
        """
        Test initialization with query parameters in the base_uri.
        """
        with pytest.raises(ValueError):
            ParliamentCommitteesAPIClient(
                f"{mock_parliament_committees_api_uri}?param=value"
            )

    def test_init_without_trailing_slash(self):
        """
        Test initialization without a trailing slash in the base_uri.
        """
        with pytest.raises(ValueError):
            client = ParliamentCommitteesAPIClient("https://example.com")

    def test_init_with_valid_base_uri(self, mock_parliament_committees_api_uri):
        """
        Test that __init__ correctly initializes ParliamentAPIClient with a valid base_uri
        """
        client = ParliamentCommitteesAPIClient(mock_parliament_committees_api_uri)

        assert client.base_uri == mock_parliament_committees_api_uri
        assert isinstance(client.session, requests.Session)

    def test_get_sub_committees(
        self, mock_parliament_committees_api_uri, mock_education_committee_id
    ):
        """
        Test that get_sub_committees correctly retrieves sub-committees for a given committee ID.
        """

        mock_response = MagicMock()
        mock_response.json.return_value = MockEducationCommittee().education_committee
        mock_response.raise_for_status.return_value = None

        with patch("requests.Session.get", return_value=mock_response):
            client = ParliamentCommitteesAPIClient(mock_parliament_committees_api_uri)
            sub_committees = client.get_sub_committees(mock_education_committee_id)

        assert len(sub_committees) > 0

    def test_get_committee_publication_list(
        self, mock_parliament_committees_api_uri, mock_education_committee_id
    ):
        """
        Test that get_committee_publication_list correctly retrieves committee publication list.
        """
        mock_response = MagicMock()
        mock_response.json.return_value = MockPublicationList().mock_publication_list
        mock_response.raise_for_status.return_value = None

        with patch("requests.Session.get", return_value=mock_response):
            client = ParliamentPublicationsAPIClient(mock_parliament_committees_api_uri)
            committee_publication_list = client.get_committee_publications_list(
                committee_id=mock_education_committee_id,
                start_date=START_DATE,
                end_date=END_DATE,
            )

        assert len(committee_publication_list.publications) > 0


class TestParliamentQuestionsApiClient:

    def test_init_creates_session_with_base_uri(
        self, mock_parliament_questions_api_uri
    ):
        """
        Test that __init__ correctly initializes ParliamentAPIClient with base_uri and creates a requests.Session
        """
        client = ParliamentQuestionsAPIClient(mock_parliament_questions_api_uri)

        assert client.base_uri == mock_parliament_questions_api_uri
        assert isinstance(client.session, requests.Session)

    def test_init_session_creation_failure(
        self, monkeypatch, mock_parliament_questions_api_uri
    ):
        """
        Test initialization when session creation fails.
        """

        def mock_session(*args, **kwargs):
            raise requests.exceptions.RequestException("Failed to create session")

        monkeypatch.setattr(requests, "Session", mock_session)
        with pytest.raises(requests.exceptions.RequestException):
            ParliamentQuestionsAPIClient(mock_parliament_questions_api_uri)

    def test_init_with_empty_base_uri(self):
        """
        Test initialization with an empty base_uri.
        """
        with pytest.raises(ValueError):
            ParliamentQuestionsAPIClient("")

    def test_init_with_invalid_uri(self):
        """
        Test initialization with an invalid URI.
        """
        with pytest.raises(ValueError):
            ParliamentQuestionsAPIClient("not_a_valid_uri")

    def test_init_with_fragment(self, mock_parliament_questions_api_uri):
        """
        Test initialization with a URL fragment in the base_uri.
        """
        with pytest.raises(ValueError):
            ParliamentQuestionsAPIClient(
                f"{mock_parliament_questions_api_uri}#fragment"
            )

    def test_init_with_non_http_protocol(self):
        """
        Test initialization with a non-HTTP protocol.
        """
        with pytest.raises(ValueError):
            ParliamentQuestionsAPIClient("ftp://example.com")

    def test_init_with_query_parameters(self, mock_parliament_questions_api_uri):
        """
        Test initialization with query parameters in the base_uri.
        """
        with pytest.raises(ValueError):
            ParliamentQuestionsAPIClient(
                f"{mock_parliament_questions_api_uri}?param=value"
            )

    def test_init_without_trailing_slash(self):
        """
        Test initialization without a trailing slash in the base_uri.
        """
        with pytest.raises(ValueError):
            client = ParliamentQuestionsAPIClient("https://example.com")

    def test_init_with_valid_base_uri(self, mock_parliament_questions_api_uri):
        """
        Test that __init__ correctly initializes ParliamentAPIClient with a valid base_uri
        """
        client = ParliamentQuestionsAPIClient(mock_parliament_questions_api_uri)

        assert client.base_uri == mock_parliament_questions_api_uri
        assert isinstance(client.session, requests.Session)

    def test_get_questions_by_date_tabled_success(
        self, mock_parliament_questions_api_uri
    ):
        """
        Test successful retrieval of questions by date tabled.
        """
        mock_response = MagicMock()
        mock_response.json.return_value = MockAPIQuestions().mock_api_questions
        mock_response.raise_for_status.return_value = None

        with patch("requests.Session.get", return_value=mock_response):
            client = ParliamentQuestionsAPIClient(mock_parliament_questions_api_uri)
            questions = client.get_questions_by_date(date_type=DATE_TYPE, start_date=START_DATE, end_date=END_DATE)

        assert len(questions.questions) == 20
        assert questions.questions[0].id == 1679703

    @patch("requests.Session.get")
    def test_get_questions_by_date_tabled_empty_response(
        self, mock_get, mock_parliament_questions_api_uri
    ):
        """
        Test get_questions_by_date_tabled when the API returns an empty response
        """
        mock_response = Mock()
        mock_response.json.return_value = {"results": [], "totalResults": 0}
        mock_get.return_value = mock_response

        client = ParliamentQuestionsAPIClient(mock_parliament_questions_api_uri)
        result = list(
            client.get_questions_by_date(date_type=DATE_TYPE, start_date=date(2024, 1, 1), end_date=date(2024, 1, 7))
        )
        assert len(result) == 0

    @patch("requests.Session.get")
    def test_get_questions_by_date_tabled_http_error(
        self, mock_get, mock_parliament_questions_api_uri
    ):
        """
        Test get_questions_by_date_tabled when an HTTP error occurs
        """
        mock_get.side_effect = requests.RequestException("HTTP Error")
        client = ParliamentQuestionsAPIClient(mock_parliament_questions_api_uri)
        with pytest.raises(requests.RequestException):
            list(
                client.get_questions_by_date(date_type=DATE_TYPE, start_date=date(2023, 1, 1), end_date=date(2023, 1, 2))
            )

    @patch("requests.Session.get")
    def test_get_questions_by_date_tabled_malformed_response(
        self, mock_get, mock_parliament_questions_api_uri
    ):
        """
        Test get_questions_by_date_tabled when the API returns a malformed response
        """
        mock_response = Mock()
        mock_response.json.return_value = {"invalid_key": "invalid_value"}
        mock_get.return_value = mock_response

        client = ParliamentQuestionsAPIClient(mock_parliament_questions_api_uri)
        with pytest.raises(KeyError):
            list(
                client.get_questions_by_date(date_type=DATE_TYPE, start_date=date(2023, 1, 1), end_date=date(2023, 1, 2))
            )

    def test_get_questions_by_date_tabled_with_empty_dates(
        self, mock_parliament_questions_api_uri
    ):
        """
        Test get_questions_by_date_tabled with empty date inputs
        """
        client = ParliamentQuestionsAPIClient(mock_parliament_questions_api_uri)
        with pytest.raises(ValueError):
            list(client.get_questions_by_date(date_type=DateType.ANSWERED, start_date="", end_date=""))

    def test_get_questions_by_date_tabled_with_end_date_before_start_date(
        self, mock_parliament_questions_api_uri
    ):
        """
        Test get_questions_by_date_tabled with end date before start date
        """
        client = ParliamentQuestionsAPIClient(mock_parliament_questions_api_uri)
        # amazonq-ignore-next-line
        end_date = date.today()
        start_date = end_date + timedelta(days=1)
        with pytest.raises(ValueError):
            list(client.get_questions_by_date(date_type=DATE_TYPE, start_date=start_date, end_date=end_date))

    def test_get_questions_by_date_tabled_with_future_dates(
        self, mock_parliament_questions_api_uri
    ):
        """
        Test get_questions_by_date_tabled with future dates
        """
        client = ParliamentQuestionsAPIClient(mock_parliament_questions_api_uri)
        # amazonq-ignore-next-line
        future_date = date.today() + timedelta(days=30)
        with pytest.raises(ValueError):
            list(client.get_questions_by_date(date_type=DATE_TYPE, start_date=future_date, end_date=future_date))

    def test_get_questions_by_date_tabled_json_decode_error(
        self, mock_parliament_questions_api_uri
    ):
        """
        Test get_questions_by_date_tabled handling of JSON decode error
        """
        client = ParliamentQuestionsAPIClient(mock_parliament_questions_api_uri)
        with patch.object(client.session, "get") as mock_get:
            mock_response = MagicMock()
            mock_response.json.side_effect = ValueError("Invalid JSON")
            mock_get.return_value = mock_response
            with pytest.raises(ValueError):
                list(client.get_questions_by_date(date_type=DATE_TYPE, start_date=START_DATE, end_date=END_DATE))
