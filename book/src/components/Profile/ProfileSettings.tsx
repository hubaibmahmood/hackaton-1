import React, { useState, useEffect } from 'react';
import { useProfile } from '../../hooks/useProfile';
import { ProfileForm, ProfileFormData } from '../Auth/ProfileForm';
import { ErrorMessage } from '../common/ErrorMessage';
import LoadingSpinner from '../common/LoadingSpinner';
import styles from './ProfileSettings.module.css';

export const ProfileSettings: React.FC = () => {
  const { data: profile, isLoading, error, updateProfile } = useProfile();
  const [updateSuccess, setUpdateSuccess] = useState(false);

  // Reset success message after 3 seconds
  useEffect(() => {
    if (updateSuccess) {
      const timer = setTimeout(() => setUpdateSuccess(false), 3000);
      return () => clearTimeout(timer);
    }
  }, [updateSuccess]);

  const handleUpdate = async (formData: ProfileFormData) => {
    try {
      await updateProfile({
        programmingLanguages: formData.programming_languages,
        frameworks: formData.frameworks,
        softwareExperienceYears: formData.software_experience_years,
        roboticsPlatforms: formData.robotics_platforms,
        sensorsActuators: formData.sensors_actuators,
        hardwareExperienceYears: formData.hardware_experience_years,
      });
      setUpdateSuccess(true);
    } catch (err) {
      // Error handled by hook
    }
  };

  if (isLoading && !profile) {
    return (
      <div className="flex justify-center p-8">
        <LoadingSpinner />
      </div>
    );
  }

  if (!profile && !isLoading) {
    return <ErrorMessage message={error || 'Failed to load profile'} />;
  }

  return (
    <div className={styles.container}>
      <div className={styles.header}>
        <h1 className={styles.title}>Profile Settings</h1>
        <div className={styles.levelBadge}>
          Current Level: <strong>{profile?.derivedExperienceLevel}</strong>
        </div>
      </div>

      {updateSuccess && (
        <div className="bg-green-100 border border-green-400 text-green-700 px-4 py-3 rounded relative mb-4" role="alert">
          <strong className="font-bold">Success!</strong>
          <span className="block sm:inline"> Profile updated successfully. Content will be re-personalized.</span>
        </div>
      )}
      
      {error && <ErrorMessage message={error} />}

      <div className={styles.formContainer}>
        <ProfileForm
          initialData={{
            programming_languages: profile?.programmingLanguages,
            frameworks: profile?.frameworks,
            software_experience_years: profile?.softwareExperienceYears,
            robotics_platforms: profile?.roboticsPlatforms,
            sensors_actuators: profile?.sensorsActuators,
            hardware_experience_years: profile?.hardwareExperienceYears,
          }}
          onSubmit={handleUpdate}
          loading={isLoading}
          submitLabel="Save Changes"
        />
      </div>
    </div>
  );
};
