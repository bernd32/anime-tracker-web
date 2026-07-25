'use client';

import { useAuthSession } from '@/features/auth/hooks';

const LOGIN_REQUIRED_MESSAGE = 'Please log in to perform actions';

export function useRequireOwnerAction() {
  const authQuery = useAuthSession();
  const canWrite = authQuery.data?.can_write ?? false;

  const requireOwnerAction = () => {
    if (!canWrite) {
      window.alert(LOGIN_REQUIRED_MESSAGE);
      return false;
    }
    return true;
  };

  return { canWrite, requireOwnerAction };
}
