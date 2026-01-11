export interface Command {
  id: string
  category: string
  sub?: string
  scene: string
  command: string
  params?: string
  notes?: string
  danger?: boolean
  warning?: string
}

export type CategoryType = 'all' | string
