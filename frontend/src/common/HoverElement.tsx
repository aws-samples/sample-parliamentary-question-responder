import { Popover, PopoverProps } from "@cloudscape-design/components";
import { useEffect, useRef, useState } from "react";

const mouseClickEvents = ["mousedown", "click", "mouseup"];
function simulateMouseClick(element: HTMLDivElement | null) {
  if (element)
    mouseClickEvents.forEach((mouseEventType) =>
      element.dispatchEvent(
        new MouseEvent(mouseEventType, {
          view: window,
          bubbles: true,
          cancelable: true,
          buttons: 1,
        })
      )
    );
}

export interface HoverElementProps extends PopoverProps {
  element: React.ReactNode;
}

const HoverElement = ({
  element,
  header,
  content,
  size,
  position,
}: HoverElementProps) => {
  const elementRef: React.MutableRefObject<HTMLDivElement | null> = useRef(null);
  const elsewhereRef: React.MutableRefObject<HTMLDivElement | null> = useRef(null);
  const [hover, setHover] = useState(false);

  useEffect(() => {
    if (hover) simulateMouseClick(elementRef.current);
    else simulateMouseClick(elsewhereRef.current);
  }, [hover]);

  return (
    <div
      onMouseOver={() => setHover(true)}
      onMouseLeave={() => setHover(false)}
      ref={elsewhereRef}
    >
      <Popover
        dismissButton={false}
        position={position}
        size={size}
        triggerType="custom"
        header={header}
        content={content}
      >
        <span ref={elementRef}>{element}</span>
      </Popover>
    </div>
  );
};

export { HoverElement };
