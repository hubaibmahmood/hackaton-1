import '@testing-library/jest-dom';

// Mock scrollIntoView
Element.prototype.scrollIntoView = jest.fn();

// Mock react-markdown
jest.mock('react-markdown', () => (props) => {
  return props.children;
});