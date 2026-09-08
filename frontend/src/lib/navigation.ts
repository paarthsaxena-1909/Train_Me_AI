import type { NavItem, Role } from './types'

export const navigationByRole: Record<Role, NavItem[]> = {
  admin: [
    { label: 'Overview', to: '/admin', icon: 'grid' },
    { label: 'Products', to: '/admin/products', icon: 'book' },
  ],
  agent: [
    { label: 'Overview', to: '/agent', icon: 'grid' },
    { label: 'Products', to: '/agent/products', icon: 'book' },
  ],
}
