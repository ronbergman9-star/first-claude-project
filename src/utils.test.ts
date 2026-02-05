import { greet, add, isEven } from './utils';

describe('greet', () => {
  it('should return a greeting with the given name', () => {
    expect(greet('World')).toBe('Hello, World!');
  });

  it('should handle empty string', () => {
    expect(greet('')).toBe('Hello, !');
  });
});

describe('add', () => {
  it('should add two positive numbers', () => {
    expect(add(2, 3)).toBe(5);
  });

  it('should handle negative numbers', () => {
    expect(add(-1, -2)).toBe(-3);
  });

  it('should handle zero', () => {
    expect(add(0, 5)).toBe(5);
  });
});

describe('isEven', () => {
  it('should return true for even numbers', () => {
    expect(isEven(2)).toBe(true);
    expect(isEven(0)).toBe(true);
    expect(isEven(-4)).toBe(true);
  });

  it('should return false for odd numbers', () => {
    expect(isEven(1)).toBe(false);
    expect(isEven(3)).toBe(false);
    expect(isEven(-7)).toBe(false);
  });
});
