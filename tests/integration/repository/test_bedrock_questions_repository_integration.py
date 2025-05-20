import pytest
import os

import sys
sys.path.append('.')
sys.path.append(os.path.join(os.getcwd(), 'layers', 'pq-responder'))

from repositories import BedrockFlow

@pytest.mark.usefixtures("aws_region", "stack_name")
class TestBedrockQuestionsRepository():

    def test_get_questions_by_subject(self, populate_knowledge_base, similar_questions_flow_alias_id, similar_questions_flow_id):
        bedrock_knowledge_base = BedrockFlow(
            flow_alias_identifier=similar_questions_flow_alias_id,
            flow_identifier=similar_questions_flow_id
        )
        response = bedrock_knowledge_base.find_similar_questions(
            question='What is being done about poor pupil behaviour'
        )

        assert len(response.questions) > 0

