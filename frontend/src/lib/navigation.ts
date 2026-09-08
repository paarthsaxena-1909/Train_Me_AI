import type { NavItem, Role } from './types'

export const navigationByRole: Record<Role, NavItem[]> = {
  admin: [
    { label: 'Overview', to: '/admin', icon: 'grid' },
    { label: 'Playbooks', to: '/admin/playbooks', icon: 'book' },
    { label: 'Conversations', to: '/admin/conversations', icon: 'chat' },
    { label: 'Team', to: '/admin/team', icon: 'users' },
  ],
  agent: [
    { label: 'Overview', to: '/agent', icon: 'grid' },
    { label: 'My playbooks', to: '/agent/playbooks', icon: 'book' },
    { label: 'Conversations', to: '/agent/conversations', icon: 'chat' },
  ],
}
