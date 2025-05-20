// Copyright Amazon.com, Inc. or its affiliates. All Rights Reserved.
// SPDX-License-Identifier: MIT-0
import { useEffect, useRef, useState } from 'react';

import Container from '@cloudscape-design/components/container';
import FormField from '@cloudscape-design/components/form-field';
import Header from '@cloudscape-design/components/header';
import Link from '@cloudscape-design/components/link';
import PromptInput from '@cloudscape-design/components/prompt-input';

import { FittedContainer, ScrollableContainer } from './common-components';
import {
  AgentResponse,
  getLoadingMessage,
  INITIAL_MESSAGES,
  Message,
} from './config';
import Messages from './messages';

import '../../styles/chat.scss';
import { ContentLayout } from '@cloudscape-design/components';
import { useAuth } from 'react-oidc-context';
import { APIFetch } from '../../api/Api';

const SuggestAnswers = () =>{
  const [messages, setMessages] = useState(INITIAL_MESSAGES);
  const [prompt, setPrompt] = useState('');
  const [isGenAiResponseLoading, setIsGenAiResponseLoading] = useState(false);
  const [session_id, setSessionId] = useState<string>('');

  const messagesContainerRef = useRef<HTMLDivElement>(null);
  const lastMessageContent = messages[messages.length - 1].content;
  const auth = useAuth();

  const isVisualRefresh = true;

  useEffect(() => {
    // Scroll to the bottom to show the new/latest message
    setTimeout(() => {
      if (messagesContainerRef.current) {
        messagesContainerRef.current.scrollTop = messagesContainerRef.current.scrollHeight;
      }
    }, 0);
  }, [lastMessageContent]);

  const onPromptSend = async ({ detail: { value } }: { detail: { value: string } }) => {
    if (!value || value.length === 0 || isGenAiResponseLoading) {
      return;
    }

    const newMessage: Message = {
      type: 'chat-bubble',
      authorId: 'user',
      content: value,
      timestamp: new Date().toLocaleTimeString(),
    };

    setMessages(prevMessages => [...prevMessages, newMessage]);
    setPrompt('');

    // Show loading state
    setIsGenAiResponseLoading(true);
    setMessages(prevMessages => [...prevMessages, getLoadingMessage()]);

    const queryString = messages.length <= 1 ? "suggest-answer" : `suggest-answer?session_id=${session_id}`

    await APIFetch(queryString, auth.user?.id_token as string, JSON.stringify({prompt: value}), 'POST')
      .then((res: AgentResponse) => {

        const newMessage: Message = {
          type: 'chat-bubble',
          authorId: 'gen-ai',
          content: res.completion,
          timestamp: new Date().toLocaleTimeString(),
        }
        setMessages((prevMessages) => [
          ...prevMessages.slice(0, -1),
          newMessage,
        ]);
        setSessionId(res.sessionId);
      })
      .catch((err) => console.log(err));

    setIsGenAiResponseLoading(false);
  };

  const generateAuthor = () => {
    const email = auth.user?.profile.email;
    return {
      username: email?.split('@')[0] as string,
      initials: email?.split('@')[0][0].toUpperCase() as string
    }
  };

  return (
    <ContentLayout
      defaultPadding
      headerVariant="high-contrast"
      header={<Header variant="h1" description="Ask anything related to the UK Government">Generative AI chat</Header>}
    >
      <div className={`chat-container ${!isVisualRefresh && 'classic'}`}>
        <FittedContainer>
          <Container            
            fitHeight
            disableContentPaddings
            footer={
              <FormField
                stretch
                constraintText={
                  <>
                    Use of this service is subject to the{' '}
                    <Link href="#" external variant="primary" fontSize="inherit">
                      AWS Responsible AI Policy
                    </Link>
                    .
                    This tool contains Parliamentary information licensed under the {' '}
                    <Link href="https://www.parliament.uk/site-information/copyright-parliament/open-parliament-licence/" external fontSize="inherit">
                      Open Parliament Licence v3.0
                    </Link>
                    .
                  </>
                }
              >
                <PromptInput
                  onChange={({ detail }) => setPrompt(detail.value)}
                  onAction={onPromptSend}
                  value={prompt}
                  actionButtonAriaLabel={isGenAiResponseLoading ? 'Send message button - suppressed' : 'Send message'}
                  actionButtonIconName="send"
                  ariaLabel={isGenAiResponseLoading ? 'Prompt input - suppressed' : 'Prompt input'}
                  placeholder="Ask a question"
                  autoFocus
                />
              </FormField>
            }
          >
            <ScrollableContainer ref={messagesContainerRef}>
              <Messages messages={messages} authorInfo={generateAuthor()}/>
            </ScrollableContainer>
          </Container>
        </FittedContainer>
      </div>
    </ContentLayout>
  );
}

export default SuggestAnswers;
