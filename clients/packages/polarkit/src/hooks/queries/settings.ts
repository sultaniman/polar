import { useQuery } from '@tanstack/react-query'
import { api } from '../../api'
import { Platforms } from '../../api/client'
import { defaultRetry } from './retry'

export const useBadgeSettings = (platform: Platforms, orgName: string) =>
  useQuery(
    ['organizationBadgeSettings'],
    () =>
      api.organizations.getBadgeSettings({
        platform: platform,
        orgName: orgName,
      }),
    {
      retry: defaultRetry,
    },
  )
