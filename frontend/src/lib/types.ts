export type Role = 'admin' | 'agent'

export type Session = {
  email: string
  role: Role
  token?: string
}

export type NavItem = {
  label: string
  to: string
  icon: string
}
