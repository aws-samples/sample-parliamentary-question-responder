// Copyright Amazon.com, Inc. or its affiliates. All Rights Reserved.
// SPDX-License-Identifier: MIT-0

import ChatBubble from '@cloudscape-design/chat-components/chat-bubble';
import { ChatBubbleAvatar } from './common-components';
import { AUTHORS, Message } from './config';

import '../../styles/chat.scss';

interface MessagesProps {
  messages: Array<Message>;
  authorInfo: {
    username: string;
    initials: string;
  }
}

export default function Messages({ messages = [], authorInfo: {username, initials} }: MessagesProps) {

  return (
    <div className="messages" role="region" aria-label="Chat">

      {messages.map((message) => {
        if (message.type === 'alert') {
          return null;
        }

        const author = AUTHORS[message.authorId];

        if (author.type === 'user') {
          author.initials = initials;
          author.name = username;
        }

        return (
          <ChatBubble
            key={message.authorId + message.timestamp}
            avatar={<ChatBubbleAvatar {...author} loading={message.avatarLoading} />}
            ariaLabel={`${author.name} at ${message.timestamp}`}
            type={author.type === 'gen-ai' ? 'incoming' : 'outgoing'}
            hideAvatar={message.hideAvatar}
            actions={message.actions}
          >
            {message.content}
          </ChatBubble>
        );
      })}
    </div>
  );
}