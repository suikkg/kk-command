<script setup lang="ts">
import { onMounted, ref } from 'vue'
import { useDark, useToggle } from '@vueuse/core'
import CommandCard from '@/components/CommandCard.vue'
import CommandModal from '@/components/CommandModal.vue'
import { useCommandStore } from '@/stores/command'
import type { Command } from '@/types/command'

const store = useCommandStore()
const selectedCommand = ref<Command | null>(null)

const isDark = useDark({
  selector: 'body',
  attribute: 'class',
  valueLight: 'light',
  valueDark: 'dark',
  storageKey: 'cmd-cheatsheet-theme',
})
const toggleDark = useToggle(isDark)

onMounted(() => {
  store.loadCommands()
})

function openModal(command: Command) {
  selectedCommand.value = command
}

function closeModal() {
  selectedCommand.value = null
}

function handleSearchEnter() {
  store.addHistory(store.searchQuery)
}

function useHistory(term: string) {
  store.searchQuery = term
}

function clearSearch() {
  store.clearSearch()
}

function handleFavOnly(event: Event) {
  const checked = (event.target as HTMLInputElement).checked
  store.setFavOnly(checked)
}
</script>

<template>
  <div class="min-h-screen bg-gradient-to-b from-slate-50 via-white to-white px-4 py-8 dark:from-slate-950 dark:via-slate-900 dark:to-slate-900">
    <div class="mx-auto flex max-w-6xl flex-col gap-6">
      <header class="flex flex-col gap-3 md:flex-row md:items-center md:justify-between">
        <div>
          <p class="text-xs uppercase tracking-[0.18em] text-blue-500">命令速查工具</p>
          <h1 class="mt-1 text-3xl font-semibold text-slate-900 dark:text-slate-50">离线 · 即搜即用</h1>
          <p class="text-sm text-slate-500 dark:text-slate-400">
            Linux / 固件分析 / Selenium / RIDE / Git · 搜索、分类、收藏、复制一站搞定
          </p>
        </div>
        <div class="flex flex-wrap items-center gap-2">
          <a
            href="/man-mirror/index.html"
            target="_blank"
            rel="noreferrer"
            class="btn-ghost"
          >
            原站镜像
          </a>
          <button class="btn-ghost" type="button" @click="toggleDark()">
            {{ isDark ? '切换到亮色' : '切换到暗色' }}
          </button>
        </div>
      </header>

      <section class="card-surface space-y-4 p-4 md:p-5">
        <div class="flex flex-col gap-3 md:flex-row md:items-center">
          <div class="flex flex-1 items-center gap-2">
            <input
              v-model="store.searchQuery"
              type="search"
              placeholder="搜索命令 / 场景 / 分类"
              class="w-full rounded-xl border border-slate-200 bg-white px-4 py-3 text-base text-slate-900 shadow-sm outline-none transition focus:border-blue-400 focus:ring-2 focus:ring-blue-100 dark:border-slate-700 dark:bg-slate-900 dark:text-slate-50 dark:focus:border-blue-500 dark:focus:ring-blue-900/40"
              @keyup.enter="handleSearchEnter"
            />
            <button class="btn-ghost" type="button" @click="clearSearch">清空</button>
          </div>
          <label class="flex items-center gap-2 text-sm text-slate-600 dark:text-slate-300">
            <input
              :checked="store.favOnly"
              type="checkbox"
              class="h-4 w-4 accent-blue-600"
              @change="handleFavOnly"
            />
            只看收藏
          </label>
        </div>

        <div class="flex flex-wrap items-center gap-2">
          <span class="text-xs uppercase tracking-wide text-slate-500 dark:text-slate-400">历史搜索</span>
          <button v-for="term in store.history" :key="term" class="chip" type="button" @click="useHistory(term)">
            {{ term }}
          </button>
          <span v-if="!store.history.length" class="text-sm text-slate-500 dark:text-slate-400">暂无记录</span>
        </div>

        <div class="flex gap-2 overflow-x-auto pb-1">
          <button
            v-for="cat in store.categories"
            :key="cat"
            class="rounded-full px-4 py-2 text-sm font-medium transition"
            :class="[
              store.activeCategory === cat
                ? 'bg-blue-600 text-white shadow-sm dark:bg-blue-500'
                : 'bg-slate-100 text-slate-700 hover:bg-slate-200 dark:bg-slate-800 dark:text-slate-200 dark:hover:bg-slate-700',
            ]"
            type="button"
            @click="store.setCategory(cat)"
          >
            {{ cat === 'all' ? '全部' : cat }}
          </button>
        </div>
      </section>

      <section class="pb-12">
        <div v-if="store.error" class="card-surface p-5 text-sm text-amber-700 dark:text-amber-300">
          {{ store.error }}
        </div>

        <div v-else-if="store.isLoading" class="text-sm text-slate-500 dark:text-slate-400">
          数据加载中...
        </div>

        <div v-else>
          <div class="mb-3 flex items-center justify-between text-sm text-slate-500 dark:text-slate-400">
            <span>共 {{ store.filteredCommands.length }} 条命令</span>
            <span v-if="store.favOnly" class="text-amber-600">已开启“只看收藏”</span>
          </div>

          <div v-if="store.filteredCommands.length" class="grid gap-4 sm:grid-cols-2 lg:grid-cols-3">
            <CommandCard
              v-for="cmd in store.filteredCommands"
              :key="cmd.id"
              :command="cmd"
              @open="openModal"
            />
          </div>

          <div v-else class="card-surface flex flex-col items-center gap-2 p-6 text-center text-slate-500 dark:text-slate-400">
            <p>未找到匹配的命令。</p>
            <p class="text-sm">试试调整关键词或切换分类。</p>
          </div>
        </div>
      </section>
    </div>

    <CommandModal v-if="selectedCommand" :command="selectedCommand" @close="closeModal" />
  </div>
</template>
