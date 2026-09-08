import { navigationByRole } from './navigation'
import type { Role } from './types'

export const routeMetadata = {
  '/': { title: 'Workspace' },
  '/admin': { title: 'Admin workspace', role: 'admin' as Role, navigation: navigationByRole.admin },
  '/agent': { title: 'Agent workspace', role: 'agent' as Role, navigation: navigationByRole.agent },
}
