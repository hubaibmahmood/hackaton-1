import { useState, useEffect, useCallback } from 'react';

interface SelectionState {
  text: string;
  range: Range | null;
  rect: DOMRect | null;
  isCollapsed: boolean;
}

export function useTextSelection() {
  const [selection, setSelection] = useState<SelectionState>({
    text: '',
    range: null,
    rect: null,
    isCollapsed: true,
  });

  const handleSelectionChange = useCallback(() => {
    const domSelection = window.getSelection();

    if (!domSelection || domSelection.rangeCount === 0 || domSelection.isCollapsed) {
      setSelection({
        text: '',
        range: null,
        rect: null,
        isCollapsed: true,
      });
      return;
    }

    const range = domSelection.getRangeAt(0);
    const text = range.toString().trim();
    const rect = range.getBoundingClientRect();

    if (text.length > 0) {
      setSelection({
        text,
        range,
        rect,
        isCollapsed: false,
      });
    } else {
      setSelection({
        text: '',
        range: null,
        rect: null,
        isCollapsed: true,
      });
    }
  }, []);

  useEffect(() => {
    document.addEventListener('selectionchange', handleSelectionChange);
    // Handle touch events for mobile selection
    document.addEventListener('touchend', handleSelectionChange);
    document.addEventListener('keyup', handleSelectionChange);
    document.addEventListener('mouseup', handleSelectionChange);

    return () => {
      document.removeEventListener('selectionchange', handleSelectionChange);
      document.removeEventListener('touchend', handleSelectionChange);
      document.removeEventListener('keyup', handleSelectionChange);
      document.removeEventListener('mouseup', handleSelectionChange);
    };
  }, [handleSelectionChange]);

  return selection;
}
