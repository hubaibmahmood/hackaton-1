import { renderHook, act } from '@testing-library/react';
import { useTextSelection } from '../../src/hooks/useTextSelection';

describe('useTextSelection', () => {
  // Mock window.getSelection
  const mockGetSelection = jest.fn();
  const originalGetSelection = window.getSelection;

  beforeAll(() => {
    window.getSelection = mockGetSelection;
  });

  afterAll(() => {
    window.getSelection = originalGetSelection;
  });

  beforeEach(() => {
    mockGetSelection.mockClear();
  });

  test('initial state is empty', () => {
    mockGetSelection.mockReturnValue({
      rangeCount: 0,
      isCollapsed: true,
      toString: () => '',
    });

    const { result } = renderHook(() => useTextSelection());

    expect(result.current.text).toBe('');
    expect(result.current.isCollapsed).toBe(true);
  });

  test('updates state on selection change', () => {
    // Mock selection
    const mockRange = {
      toString: () => 'Selected Text',
      getBoundingClientRect: () => ({
        top: 10,
        left: 10,
        width: 100,
        height: 20,
      }),
    };

    mockGetSelection.mockReturnValue({
      rangeCount: 1,
      isCollapsed: false,
      getRangeAt: () => mockRange,
      toString: () => 'Selected Text',
    });

    const { result } = renderHook(() => useTextSelection());

    // Trigger selectionchange event
    act(() => {
      document.dispatchEvent(new Event('selectionchange'));
    });

    expect(result.current.text).toBe('Selected Text');
    expect(result.current.isCollapsed).toBe(false);
    expect(result.current.rect).toEqual(expect.objectContaining({
      top: 10,
      left: 10,
    }));
  });

  test('clears selection when collapsed', () => {
    // First set a selection
    mockGetSelection.mockReturnValue({
      rangeCount: 1,
      isCollapsed: false,
      getRangeAt: () => ({
        toString: () => 'Text',
        getBoundingClientRect: () => ({}),
      }),
      toString: () => 'Text',
    });

    const { result } = renderHook(() => useTextSelection());

    act(() => {
      document.dispatchEvent(new Event('selectionchange'));
    });

    expect(result.current.text).toBe('Text');

    // Now collapse it
    mockGetSelection.mockReturnValue({
      rangeCount: 1,
      isCollapsed: true, // Collapsed
      toString: () => '',
    });

    act(() => {
      document.dispatchEvent(new Event('selectionchange'));
    });

    expect(result.current.text).toBe('');
    expect(result.current.isCollapsed).toBe(true);
  });
});
