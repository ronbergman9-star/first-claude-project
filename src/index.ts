import { greet, add } from './utils';

function main(): void {
  const message = greet('World');
  // eslint-disable-next-line no-console
  console.log(message);

  const result = add(2, 3);
  // eslint-disable-next-line no-console
  console.log(`2 + 3 = ${result}`);
}

main();
