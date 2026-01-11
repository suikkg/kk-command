import { computed, ref } from 'vue'
import { defineStore } from 'pinia'
import { useStorage } from '@vueuse/core'
import type { CategoryType, Command } from '@/types/command'

const FAVORITES_KEY = 'cmd-cheatsheet-favorites'
const HISTORY_KEY = 'cmd-cheatsheet-history'
const LAST_SEARCH_KEY = 'cmd-cheatsheet-last-search'
const FAV_ONLY_KEY = 'cmd-cheatsheet-fav-only'

export const useCommandStore = defineStore('commands', () => {
  const commands = ref<Command[]>([])
  const isLoading = ref(false)
  const error = ref<string | null>(null)

  const searchQuery = useStorage<string>(LAST_SEARCH_KEY, '')
  const activeCategory = ref<CategoryType>('all')
  const favOnly = useStorage<boolean>(FAV_ONLY_KEY, false)

  const favorites = useStorage<string[]>(FAVORITES_KEY, [])
  const history = useStorage<string[]>(HISTORY_KEY, [])

  const favoriteSet = computed(() => new Set(favorites.value))

  const categories = computed(() => {
    const set = new Set<string>(commands.value.map((c) => c.category))
    return ['all', ...Array.from(set)]
  })

  const filteredCommands = computed(() => {
    const keyword = searchQuery.value.trim().toLowerCase()

    return commands.value.filter((cmd) => {
      const matchCategory = activeCategory.value === 'all' || cmd.category === activeCategory.value
      const matchFavorite = !favOnly.value || favoriteSet.value.has(cmd.id)
      const haystack = `${cmd.scene} ${cmd.command} ${cmd.category} ${cmd.sub ?? ''} ${cmd.params ?? ''} ${
        cmd.notes ?? ''
      }`.toLowerCase()
      const matchKeyword = !keyword || haystack.includes(keyword)
      return matchCategory && matchFavorite && matchKeyword
    })
  })

  async function loadCommands() {
    if (commands.value.length) return
    isLoading.value = true
    error.value = null
    try {
      const res = await fetch('/data.json')
      if (!res.ok) throw new Error(`HTTP ${res.status}`)
      const data: Command[] = await res.json()
      commands.value = data
    } catch (err) {
      console.error('加载 data.json 失败', err)
      error.value = '数据加载失败，请检查 data.json 是否可访问。'
    } finally {
      isLoading.value = false
    }
  }

  function toggleFavorite(id: string) {
    const set = new Set(favoriteSet.value)
    if (set.has(id)) set.delete(id)
    else set.add(id)
    favorites.value = Array.from(set)
  }

  function addHistory(term: string) {
    const keyword = term.trim()
    if (!keyword) return
    const existing = history.value.filter((item) => item !== keyword)
    history.value = [keyword, ...existing].slice(0, 8)
  }

  function setCategory(category: CategoryType) {
    activeCategory.value = category
  }

  function clearSearch() {
    searchQuery.value = ''
  }

  function setFavOnly(value: boolean) {
    favOnly.value = value
  }

  return {
    commands,
    filteredCommands,
    categories,
    searchQuery,
    activeCategory,
    favOnly,
    favorites,
    history,
    isLoading,
    error,
    favoriteSet,
    loadCommands,
    toggleFavorite,
    addHistory,
    setCategory,
    clearSearch,
    setFavOnly,
  }
})
