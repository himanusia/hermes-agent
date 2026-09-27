export function createPendingDeepLinkQueue<T>() {
  let pending: T[] = []

  return {
    enqueue(link: T): void {
      pending.push(link)
    },
    takeAll(): T[] {
      const drained = pending
      pending = []

      return drained
    }
  }
}
