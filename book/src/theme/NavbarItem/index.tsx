import React, {type ReactNode} from 'react';
import NavbarItem from '@theme-original/NavbarItem';
import type NavbarItemType from '@theme/NavbarItem';
import type {WrapperProps} from '@docusaurus/types';
import ProfileIcon from '../../components/Profile/ProfileIcon';
import AuthButtons from '../../components/Auth/AuthButtons';

type Props = WrapperProps<typeof NavbarItemType>;

export default function NavbarItemWrapper(props: Props): ReactNode {
  if (props.type === 'custom-profile') {
    return <ProfileIcon />;
  }
  if (props.type === 'custom-auth-buttons') {
    return <AuthButtons />;
  }
  return (
    <>
      <NavbarItem {...props} />
    </>
  );
}
