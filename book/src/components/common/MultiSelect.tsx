/**
 * Multi-select dropdown component.
 * Allows users to select multiple options from a list.
 */
import React, { useState, useRef, useEffect } from 'react';
import styles from './MultiSelect.module.css';

interface MultiSelectProps {
  options: string[];
  selected: string[];
  onChange: (selected: string[]) => void;
  placeholder?: string;
  disabled?: boolean;
  maxItems?: number;
}

export const MultiSelect: React.FC<MultiSelectProps> = ({
  options,
  selected,
  onChange,
  placeholder = 'Select options',
  disabled = false,
  maxItems = 20,
}) => {
  const [isOpen, setIsOpen] = useState(false);
  const containerRef = useRef<HTMLDivElement>(null);

  // Close dropdown when clicking outside
  useEffect(() => {
    const handleClickOutside = (event: MouseEvent) => {
      if (containerRef.current && !containerRef.current.contains(event.target as Node)) {
        setIsOpen(false);
      }
    };

    document.addEventListener('mousedown', handleClickOutside);
    return () => document.removeEventListener('mousedown', handleClickOutside);
  }, []);

  const handleToggle = () => {
    if (!disabled) {
      setIsOpen(!isOpen);
    }
  };

  const handleSelect = (option: string) => {
    if (selected.includes(option)) {
      // Remove if already selected
      onChange(selected.filter((item) => item !== option));
    } else {
      // Add if not selected (check max limit)
      if (selected.length < maxItems) {
        onChange([...selected, option]);
      }
    }
  };

  const handleRemove = (option: string, e: React.MouseEvent) => {
    e.stopPropagation();
    onChange(selected.filter((item) => item !== option));
  };

  const handleClear = (e: React.MouseEvent) => {
    e.stopPropagation();
    onChange([]);
  };

  return (
    <div className={styles.container} ref={containerRef}>
      <div
        className={`${styles.selector} ${disabled ? styles.disabled : ''} ${
          isOpen ? styles.open : ''
        }`}
        onClick={handleToggle}
      >
        <div className={styles.selectedItems}>
          {selected.length === 0 ? (
            <span className={styles.placeholder}>{placeholder}</span>
          ) : (
            selected.map((item) => (
              <span key={item} className={styles.tag}>
                {item}
                {!disabled && (
                  <button
                    type="button"
                    className={styles.removeBtn}
                    onClick={(e) => handleRemove(item, e)}
                    aria-label={`Remove ${item}`}
                  >
                    ×
                  </button>
                )}
              </span>
            ))
          )}
        </div>
        <div className={styles.actions}>
          {selected.length > 0 && !disabled && (
            <button
              type="button"
              className={styles.clearBtn}
              onClick={handleClear}
              aria-label="Clear all"
            >
              Clear
            </button>
          )}
          <span className={styles.arrow}>{isOpen ? '▲' : '▼'}</span>
        </div>
      </div>

      {isOpen && (
        <div className={styles.dropdown}>
          {options.length === 0 ? (
            <div className={styles.emptyMessage}>No options available</div>
          ) : (
            options.map((option) => {
              const isSelected = selected.includes(option);
              const isDisabled = !isSelected && selected.length >= maxItems;

              return (
                <div
                  key={option}
                  className={`${styles.option} ${isSelected ? styles.selected : ''} ${
                    isDisabled ? styles.disabledOption : ''
                  }`}
                  onClick={() => !isDisabled && handleSelect(option)}
                >
                  <input
                    type="checkbox"
                    checked={isSelected}
                    onChange={() => {}}
                    disabled={isDisabled}
                    className={styles.checkbox}
                  />
                  <span className={styles.optionLabel}>{option}</span>
                </div>
              );
            })
          )}
          {selected.length >= maxItems && (
            <div className={styles.maxItemsMessage}>
              Maximum {maxItems} items can be selected
            </div>
          )}
        </div>
      )}
    </div>
  );
};
