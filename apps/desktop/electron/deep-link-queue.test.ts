import { describe, expect, it } from 'vitest'

import { createPendingDeepLinkQueue } from './deep-link-queue'

describe('createPendingDeepLinkQueue', () => {
  it('preserves every cold-start deep link in arrival order', () => {
    const queue = createPendingDeepLinkQueue<{ kind: string; name: string }>()
    const first = { kind: 'session', name: 'first' }
    const second = { kind: 'session', name: 'second' }

    queue.enqueue(first)
    queue.enqueue(second)

    expect(queue.takeAll()).toEqual([first, second])
    expect(queue.takeAll()).toEqual([])
  })

  it('keeps links enqueued after a drain for the next readiness pass', () => {
    const queue = createPendingDeepLinkQueue<string>()

    queue.enqueue('before-ready')
    expect(queue.takeAll()).toEqual(['before-ready'])

    queue.enqueue('during-next-startup')
    expect(queue.takeAll()).toEqual(['during-next-startup'])
  })
})
