import type {ReactNode} from 'react';
import clsx from 'clsx';
import Link from '@docusaurus/Link';
import useDocusaurusContext from '@docusaurus/useDocusaurusContext';
import Layout from '@theme/Layout';
import Heading from '@theme/Heading';

import styles from './index.module.css';

function HomepageHeader() {
  const {siteConfig} = useDocusaurusContext();
  return (
    <header className={clsx('hero hero--primary', styles.heroBanner)}>
      <div className="container">
        <Heading as="h1" className="hero__title">
          {siteConfig.title}
        </Heading>
        <p className="hero__subtitle">{siteConfig.tagline}</p>
        <div className={styles.buttons}>
          <Link
            className="button button--secondary button--lg"
            to="/docs/part-01-physical-ai/intro">
            Start Reading 📖
          </Link>
        </div>
      </div>
    </header>
  );
}

export default function Home(): ReactNode {
  const {siteConfig} = useDocusaurusContext();
  return (
    <Layout
      title={`${siteConfig.title}`}
      description="A comprehensive textbook for the next generation of roboticists covering Physical AI, ROS 2, Simulation, and more.">
      <HomepageHeader />
      <main>
        <div className="container padding-vert--xl">
          <div className="row">
            <div className="col col--4">
              <div className="text--center padding-horiz--md">
                <Heading as="h3">Physical AI</Heading>
                <p>Understand the principles of embodied intelligence and how AI interacts with the physical world.</p>
              </div>
            </div>
            <div className="col col--4">
              <div className="text--center padding-horiz--md">
                <Heading as="h3">ROS 2 & Simulation</Heading>
                <p>Master the Robotic Operating System and simulation environments like Gazebo and NVIDIA Isaac.</p>
              </div>
            </div>
            <div className="col col--4">
              <div className="text--center padding-horiz--md">
                <Heading as="h3">Humanoid Robotics</Heading>
                <p>Design and program humanoid robots for natural interaction and complex tasks.</p>
              </div>
            </div>
          </div>
        </div>
      </main>
    </Layout>
  );
}