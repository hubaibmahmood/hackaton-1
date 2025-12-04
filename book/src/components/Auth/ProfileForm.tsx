/**
 * Profile form component for background information.
 * Collects user's programming, robotics, and experience data.
 */
import React, { useState } from 'react';
import { Button } from '../common/Button';
import { ErrorMessage } from '../common/ErrorMessage';
import { MultiSelect } from '../common/MultiSelect';
import styles from './ProfileForm.module.css';

// Predefined options from backend
const PROGRAMMING_LANGUAGES = [
  'Python', 'C++', 'Java', 'JavaScript', 'C', 'MATLAB', 'R', 'Go', 'Rust', 'Swift',
];

const FRAMEWORKS = [
  'ROS 2', 'ROS 1', 'TensorFlow', 'PyTorch', 'OpenCV', 'Gazebo',
  'Isaac Sim', 'Unity', 'Unreal Engine', 'WebRTC',
];

const ROBOTICS_PLATFORMS = [
  'Arduino', 'Raspberry Pi', 'NVIDIA Jetson', 'Intel NUC', 'Custom PCB',
  'TurtleBot', 'UR Robot', 'Franka Emika', 'ABB Robot', 'Mobile Robot',
];

const SENSORS_ACTUATORS = [
  'LiDAR', 'Camera (RGB)', 'Depth Camera', 'IMU', 'GPS', 'Ultrasonic',
  'Servo Motors', 'Stepper Motors', 'DC Motors', 'Gripper',
];

export interface ProfileFormData {
  programming_languages: string[];
  frameworks: string[];
  software_experience_years: number;
  robotics_platforms: string[];
  sensors_actuators: string[];
  hardware_experience_years: number;
}

interface ProfileFormProps {
  onSubmit: (data: ProfileFormData) => void;
  loading?: boolean;
  error?: string | null;
  initialData?: Partial<ProfileFormData>;
  submitLabel?: string;
}

interface FormErrors {
  programming_languages?: string;
  software_experience_years?: string;
  hardware_experience_years?: string;
}

export const ProfileForm: React.FC<ProfileFormProps> = ({ 
  onSubmit, 
  loading, 
  error, 
  initialData, 
  submitLabel = "Complete Signup" 
}) => {
  const [formData, setFormData] = useState<ProfileFormData>({
    programming_languages: initialData?.programming_languages || [],
    frameworks: initialData?.frameworks || [],
    software_experience_years: initialData?.software_experience_years || 0,
    robotics_platforms: initialData?.robotics_platforms || [],
    sensors_actuators: initialData?.sensors_actuators || [],
    hardware_experience_years: initialData?.hardware_experience_years || 0,
  });

  const [errors, setErrors] = useState<FormErrors>({});
  const [touched, setTouched] = useState<Record<string, boolean>>({});

  const validateExperienceYears = (value: number, field: string): string | undefined => {
    if (value < 0) {
      return 'Experience cannot be negative';
    }
    if (value > 50) {
      return 'Experience cannot exceed 50 years';
    }
    return undefined;
  };

  const handleExperienceChange = (field: 'software_experience_years' | 'hardware_experience_years', value: string) => {
    const numValue = parseInt(value, 10) || 0;
    setFormData({ ...formData, [field]: numValue });

    if (touched[field]) {
      const error = validateExperienceYears(numValue, field);
      setErrors({ ...errors, [field]: error });
    }
  };

  const handleBlur = (field: string) => {
    setTouched({ ...touched, [field]: true });

    const newErrors: FormErrors = { ...errors };

    if (field === 'software_experience_years') {
      newErrors.software_experience_years = validateExperienceYears(
        formData.software_experience_years,
        field
      );
    } else if (field === 'hardware_experience_years') {
      newErrors.hardware_experience_years = validateExperienceYears(
        formData.hardware_experience_years,
        field
      );
    }

    setErrors(newErrors);
  };

  const handleSubmit = (e: React.FormEvent) => {
    e.preventDefault();

    // Validate all fields
    const newErrors: FormErrors = {
      software_experience_years: validateExperienceYears(
        formData.software_experience_years,
        'software_experience_years'
      ),
      hardware_experience_years: validateExperienceYears(
        formData.hardware_experience_years,
        'hardware_experience_years'
      ),
    };

    setErrors(newErrors);
    setTouched({
      software_experience_years: true,
      hardware_experience_years: true,
    });

    // Check if there are any errors
    const hasErrors = Object.values(newErrors).some((error) => error !== undefined);

    if (!hasErrors) {
      onSubmit(formData);
    }
  };

  return (
    <form onSubmit={handleSubmit} className={styles.profileForm}>
      <div className={styles.section}>
        <h3 className={styles.sectionTitle}>Software Background</h3>

        <div className={styles.formGroup}>
          <label className={styles.label}>Programming Languages</label>
          <MultiSelect
            options={PROGRAMMING_LANGUAGES}
            selected={formData.programming_languages}
            onChange={(selected) =>
              setFormData({ ...formData, programming_languages: selected })
            }
            placeholder="Select languages you know"
            disabled={loading}
          />
          <span className={styles.hint}>Select all that apply</span>
        </div>

        <div className={styles.formGroup}>
          <label className={styles.label}>Frameworks & Tools</label>
          <MultiSelect
            options={FRAMEWORKS}
            selected={formData.frameworks}
            onChange={(selected) => setFormData({ ...formData, frameworks: selected })}
            placeholder="Select frameworks you've used"
            disabled={loading}
          />
          <span className={styles.hint}>Select all that apply</span>
        </div>

        <div className={styles.formGroup}>
          <label htmlFor="software_experience" className={styles.label}>
            Software Experience (years) *
          </label>
          <input
            type="number"
            id="software_experience"
            min="0"
            max="50"
            value={formData.software_experience_years}
            onChange={(e) => handleExperienceChange('software_experience_years', e.target.value)}
            onBlur={() => handleBlur('software_experience_years')}
            className={`${styles.input} ${
              touched.software_experience_years && errors.software_experience_years
                ? styles.inputError
                : ''
            }`}
            disabled={loading}
          />
          {touched.software_experience_years && errors.software_experience_years && (
            <span className={styles.fieldError}>{errors.software_experience_years}</span>
          )}
        </div>
      </div>

      <div className={styles.section}>
        <h3 className={styles.sectionTitle}>Hardware & Robotics Background</h3>

        <div className={styles.formGroup}>
          <label className={styles.label}>Robotics Platforms</label>
          <MultiSelect
            options={ROBOTICS_PLATFORMS}
            selected={formData.robotics_platforms}
            onChange={(selected) =>
              setFormData({ ...formData, robotics_platforms: selected })
            }
            placeholder="Select platforms you've worked with"
            disabled={loading}
          />
          <span className={styles.hint}>Select all that apply</span>
        </div>

        <div className={styles.formGroup}>
          <label className={styles.label}>Sensors & Actuators</label>
          <MultiSelect
            options={SENSORS_ACTUATORS}
            selected={formData.sensors_actuators}
            onChange={(selected) =>
              setFormData({ ...formData, sensors_actuators: selected })
            }
            placeholder="Select sensors/actuators you've used"
            disabled={loading}
          />
          <span className={styles.hint}>Select all that apply</span>
        </div>

        <div className={styles.formGroup}>
          <label htmlFor="hardware_experience" className={styles.label}>
            Hardware Experience (years) *
          </label>
          <input
            type="number"
            id="hardware_experience"
            min="0"
            max="50"
            value={formData.hardware_experience_years}
            onChange={(e) => handleExperienceChange('hardware_experience_years', e.target.value)}
            onBlur={() => handleBlur('hardware_experience_years')}
            className={`${styles.input} ${
              touched.hardware_experience_years && errors.hardware_experience_years
                ? styles.inputError
                : ''
            }`}
            disabled={loading}
          />
          {touched.hardware_experience_years && errors.hardware_experience_years && (
            <span className={styles.fieldError}>{errors.hardware_experience_years}</span>
          )}
        </div>
      </div>

      {error && <ErrorMessage message={error} />}

      <div className={styles.actions}>
        <Button
          type="submit"
          variant="primary"
          fullWidth
          disabled={loading}
          isLoading={loading}
          loadingText="Processing..."
        >
          {submitLabel}
        </Button>
      </div>
    </form>
  );
};
