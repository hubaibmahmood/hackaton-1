import {themes as prismThemes} from 'prism-react-renderer';
import type {Config} from '@docusaurus/types';
import type * as Preset from '@docusaurus/preset-classic';
import path from 'path';

// This runs in Node.js - Don't use client-side code here (browser APIs, JSX...)

const config: Config = {
  title: 'Physical AI & Humanoid Robotics',
  tagline: 'A comprehensive textbook for the next generation of roboticists',
  favicon: 'img/favicon.ico',

  // Future flags, see https://docusaurus.io/docs/api/docusaurus-config#future
  future: {
    v4: true, // Improve compatibility with the upcoming Docusaurus v4
  },

  plugins: [
    function (context, options) {
      return {
        name: 'custom-alias-plugin',
        configureWebpack(config, isServer) {
          return {
            resolve: {
              alias: {
                '@': path.resolve(__dirname, './src'),
              },
            },
          };
        },
      };
    },
    // Custom plugin to inject environment variables via Webpack DefinePlugin
    function (context, options) {
      return {
        name: 'docusaurus-environment-plugin',
        configureWebpack(config, isServer) {
          if (!isServer) {
            // Only apply to client-side build
            const webpack = require('webpack');
            config.plugins.push(
              new webpack.DefinePlugin({
                'process.env.DOCUSAURUS_AUTH_SERVER_URL': JSON.stringify(process.env.DOCUSAURUS_AUTH_SERVER_URL),
                // Add other client-side environment variables here if needed
              })
            );
          }
          return config;
        },
      };
    },
  ],

  // Set the production url of your site here
  url: 'https://hubaibmahmood.github.io',
  // Set the /<baseUrl>/ pathname under which your site is served
  // For GitHub pages deployment, it is often '/<projectName>/'
  baseUrl: '/hackaton-1/',

  // GitHub pages deployment config.
  organizationName: 'hubaibmahmood', // Usually your GitHub org/user name.
  projectName: 'hackaton-1', // Usually your repo name.

  onBrokenLinks: 'throw',
  markdown: {
    hooks: {
      onBrokenMarkdownLinks: 'warn',
    },
  },

  // Even if you don't use internationalization, you can use this field to set
  // useful metadata like html lang. For example, if your site is Chinese, you
  // may want to replace "en" with "zh-Hans".
  i18n: {
    defaultLocale: 'en',
    locales: ['en'],
  },

  presets: [
    [
      'classic',
      {
        docs: {
          sidebarPath: './sidebars.ts',
          // Please change this to your repo.
          editUrl:
            'https://github.com/hubaibmahmood/hackaton-1/tree/main/book/',
        },
        blog: false, // Disable blog for textbook
        theme: {
          customCss: './src/css/custom.css',
        },
      } satisfies Preset.Options,
    ],
  ],

  themeConfig: {
    // Replace with your project's social card
    image: 'img/docusaurus-social-card.jpg',
    colorMode: {
      defaultMode: 'light',
      disableSwitch: false,
      respectPrefersColorScheme: true,
    },
    tableOfContents: {
      minHeadingLevel: 2,
      maxHeadingLevel: 3,
    },
    docs: {
      sidebar: {
        hideable: true, // Allow sidebar to be hidden
      },
    },
    navbar: {
      title: 'Physical AI & Humanoid Robotics',
      logo: {
        alt: 'Physical AI Logo',
        src: 'img/logo.svg',
      },
      items: [
        {
          type: 'docSidebar',
          sidebarId: 'tutorialSidebar',
          position: 'left',
          label: 'Read Book',
        },
        {
          href: 'https://github.com/hubaibmahmood/hackaton-1',
          label: 'GitHub',
          position: 'right',
        },
        {
          type: 'custom-auth-buttons',
          position: 'right',
        },
        {
          type: 'custom-profile',
          position: 'right',
        },
      ],
    },
    footer: {
      style: 'dark',
      links: [
        {
          title: 'Content',
          items: [
            {
              label: 'Start Reading',
              to: '/docs/part-01-physical-ai/intro',
            },
          ],
        },
        {
          title: 'Community',
          items: [
            {
              label: 'GitHub',
              href: 'https://github.com/hubaibmahmood/hackaton-1',
            },
          ],
        },
      ],
      copyright: `Copyright © ${new Date().getFullYear()} Physical AI & Humanoid Robotics Textbook. Built with Docusaurus.`,
    },
    prism: {
      theme: prismThemes.github,
      darkTheme: prismThemes.dracula,
      additionalLanguages: ['python', 'bash', 'yaml', 'json'],
    },
  } satisfies Preset.ThemeConfig,
};

export default config;
