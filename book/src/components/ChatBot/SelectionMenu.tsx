import React, { useEffect, useState } from 'react';
import { useFloating, offset, flip, shift } from '@floating-ui/react';
import './SelectionMenu.css';

interface SelectionMenuProps {
  text: string;
  rect: DOMRect | null;
  onAsk: (text: string) => void;
}

export const SelectionMenu: React.FC<SelectionMenuProps> = ({ text, rect, onAsk }) => {
  const [isOpen, setIsOpen] = useState(false);
  
  const { refs, floatingStyles } = useFloating({
    placement: 'top',
    middleware: [offset(10), flip(), shift()],
  });

  useEffect(() => {
    if (text && rect) {
      setIsOpen(true);
      // Set reference based on selection rect
      refs.setReference({
        getBoundingClientRect: () => rect,
      });
    } else {
      setIsOpen(false);
    }
  }, [text, rect, refs]);

  if (!isOpen || !text) return null;

  return (
    <div
      ref={refs.setFloating}
      style={floatingStyles}
      className="selection-menu"
    >
      <button 
        className="selection-menu-button"
        onClick={() => onAsk(text)}
      >
        <span className="selection-menu-icon">✨</span>
        Ask AI about this
      </button>
    </div>
  );
};
