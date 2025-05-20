// Copyright Amazon.com, Inc. or its affiliates. All Rights Reserved.
// SPDX-License-Identifier: MIT-0
import Box from '@cloudscape-design/components/box';

export type Message = ChatBubbleMessage | AlertMessage;

type ChatBubbleMessage = {
  type: 'chat-bubble';
  authorId: string;
  content: React.ReactNode;
  timestamp: string;
  actions?: React.ReactNode;
  hideAvatar?: boolean;
  avatarLoading?: boolean;
};

type AlertMessage = {
  type: 'alert';
  content: React.ReactNode;
  header?: string;
};

export type AgentResponse = {
  completion: string;
  sessionId: string;
}

export const getLoadingMessage = (): Message => ({
  type: 'chat-bubble',
  authorId: 'gen-ai',
  content: <Box color="text-status-inactive">Generating a response</Box>,
  timestamp: new Date().toLocaleTimeString(),
  avatarLoading: true,
});

export type AuthorAvatarProps = {
  type: 'user' | 'gen-ai';
  name: string;
  initials?: string;
  loading?: boolean;
};
type AuthorsType = {
  [key: string]: AuthorAvatarProps;
};

export const AUTHORS: AuthorsType = {
  'user': { type: 'user', name: 'Jane Doe', initials: 'JD' },
  'gen-ai': { type: 'gen-ai', name: 'Parliamentary Question Responder' },
};

export const INITIAL_MESSAGES: Array<Message> = [
  {
    type: 'chat-bubble',
    authorId: 'gen-ai',
    content: 'Hello! This is your Generative Assistant. What can I help you with today?',
    timestamp: "10",
  }
];