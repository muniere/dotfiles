export abstract class Result<T> {
  abstract value: T | undefined;
  abstract error: Error | undefined;

  map<U>(transform: (result: Result<T>) => Result<U>): Result<U> {
    return transform(this);
  }

  fold<U>(callback: {
    onSuccess: (result: T) => U;
    onFailure: (result: Error) => U;
  }): U {
    if (this instanceof Success) {
      return callback.onSuccess(this.rawValue);
    }
    if (this instanceof Failure) {
      return callback.onFailure(this.rawValue);
    }
    throw new Error();
  }

  static run<T>(fn: () => T): Result<T> {
    try {
      const result = fn();
      return new Success(result);
    } catch (error) {
      return new Failure(error);
    }
  }

  static runOr<T>(
    fn: () => T,
    options: { fallback?: () => T } = {},
  ): T | undefined {
    try {
      const result = fn();
      return result;
    } catch {
      const fallback = options.fallback;
      return fallback ? fallback() : undefined;
    }
  }
  static async runAsync<T>(fn: () => Promise<T>): Promise<Result<T>> {
    try {
      const result = await fn();
      return new Success(result);
    } catch (error) {
      return new Failure(error);
    }
  }

  static async runAsyncOr<T>(
    fn: () => Promise<T>,
    options: { fallback?: () => T } = {},
  ): Promise<T | undefined> {
    try {
      const result = await fn();
      return result;
    } catch {
      const fallback = options.fallback;
      return fallback ? fallback() : undefined;
    }
  }
}

class Success<T> extends Result<T> {
  constructor(readonly rawValue: T) {
    super();
  }

  get value(): T | undefined {
    return this.rawValue;
  }

  get error(): Error | undefined {
    return undefined;
  }
}

class Failure<T> extends Result<T> {
  constructor(readonly rawValue: Error) {
    super();
  }

  get value(): T | undefined {
    return undefined;
  }

  get error(): Error | undefined {
    return this.rawValue;
  }
}

export function run<T>(fn: () => T): T {
  return fn();
}
