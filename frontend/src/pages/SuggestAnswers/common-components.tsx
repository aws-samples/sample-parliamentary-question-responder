// Copyright Amazon.com, Inc. or its affiliates. All Rights Reserved.
// SPDX-License-Identifier: MIT-0
import { forwardRef } from 'react';

import Avatar from '@cloudscape-design/chat-components/avatar';

import { AuthorAvatarProps } from './config';

export function ChatBubbleAvatar({ type, name, initials, loading }: AuthorAvatarProps) {
  if (type === 'gen-ai') {
    return <Avatar color="gen-ai" iconName="gen-ai" tooltipText={name} ariaLabel={name} loading={loading} />;
  }

  return <Avatar initials={initials} tooltipText={name} ariaLabel={name} />;
}

export const FittedContainer = ({ children }: { children: React.ReactNode }) => {
  return (
    <>
      <div style={{ position: 'relative', flexGrow: 1}}>
        <div style={{ position: 'absolute', inset: 0 }}>{children}</div>
      </div>
    </>
  );
};

export const ScrollableContainer = forwardRef(function ScrollableContainer(
  { children }: { children: React.ReactNode },
  ref: React.Ref<HTMLDivElement>
) {
  return (
    <div style={{ position: 'relative', blockSize: '100%' }}>
      <div style={{ position: 'absolute', inset: 0, overflowY: 'auto' }} ref={ref} data-testid="chat-scroll-container">
        {children}
      </div>
    </div>
  );
});