// Generates a random integer between min (inclusive) and max (inclusive)
export function randomNumberBetween(min, max) {
    return Math.floor(Math.random() * (max - min + 1) + min);
  }
  
  // Returns a random element from the array
  export function sample(array) {
    return array[randomNumberBetween(0, array.length - 1)];
  }
  
  /**
   * Returns the first element of an array.
   * @param {Array} array The input array.
   * @param {number} n Number of elements to return (default: 1).
   * @returns {*} The first element if `n` is 1, or an array of the first `n` elements.
   * @example
   * // Example usage:
   * const arr = [1, 2, 3, 4, 5];
   * const firstElement = first(arr); // Result: 1
   * const firstThreeElements = first(arr, 3); // Result: [1, 2, 3]
   */
  export function first(array, n = 1) {
    if (n === 1) return array[0];
    return array.filter((_, index) => index < n);
  }
  
  /**
   * Returns the last element of an array.
   * @param {Array} array The input array.
   * @param {number} n Number of elements to return (default: 1).
   * @returns {*} The last element if `n` is 1, or an array of the last `n` elements.
   * @example
   * // Example usage:
   * const arr = [1, 2, 3, 4, 5];
   * const lastElement = last(arr); // Result: 5
   * const lastThreeElements = last(arr, 3); // Result: [3, 4, 5]
   */
  export function last(array, n = 1) {
    if (n === 1) return array[array.length - 1];
    return array.filter((_, index) => array.length - index <= n);
  }
  
  /**
   * Applies a function to each key-value pair in an object and returns a new object with the results.
   * 
   * @param {function} func - Function called with key and value as arguments.
   * @param {Object} obj - Original object.
   * @returns {Object} - Mapped object.
   * 
   * @example
   * const obj = { a: 1, b: 2, c: 3 };
   * const mapped = arrayMapAssoc((key, value) => `${key}_${value}`, obj);
   * console.log(mapped); // { a: 'a_1', b: 'b_2', c: 'c_3' }
   */
  export function arrayMapAssoc(func, obj) {
    return Object.fromEntries(
      Object.entries(obj).map(([key, value]) => [key, func(key, value)])
    );
  }
  
  /**
   * Sanitizes a given input by replacing special characters with their HTML encoded equivalents.
   * 
   * @param {string} input - The input string to sanitize.
   * @returns {string} - The sanitized string.
   * 
   * @example
   * let input = 'This <script>alert("Hello");</script> is a test & check';
   * let sanitized = sanitize(input);
   * console.log(sanitized); // 'This &lt;script&gt;alert(&quot;Hello&quot;);&lt;/script&gt; is a test &amp; check'
   */
  export const sanitize = (input) => {
    const encodedCharacters = {
      '&': '&amp;',
      '<': '&lt;',
      '>': '&gt;',
      '"': '&quot;',
      "'": '&#x27;',
      '/': '&#x2F;'
    };
  
    return input.replace(/[&<>"'/]/g, match => encodedCharacters[match]);
  }
  
  /**
   * Converts a given text into a slug.
   * 
   * Converts text to lowercase, removes leading/trailing whitespace,
   * replaces spaces with hyphens, removes non-word characters except hyphens,
   * and replaces consecutive hyphens with a single hyphen.
   * 
   * @param {string} text - The text to convert into a slug.
   * @returns {string} - The resulting slug.
   * 
   * @example
   * let text = "  Hello World!  ";
   * let slug = slugify(text);
   * console.log(slug); // "hello-world"
   */
  export function slugify(text) {
    return text
      .toLowerCase() // Convert to lowercase
      .trim() // Remove leading and trailing whitespace
      .replace(/\s+/g, '-') // Replace spaces with hyphens
      .replace(/[^\w-]+/g, '') // Remove non-word characters except hyphens
      .replace(/--+/g, '-'); // Replace consecutive hyphens with a single hyphen
  }
  
  /**
   * Checks if none of the elements in the array satisfy the provided predicate function.
   * 
   * @param {Function} predicate - The function to test each element.
   * @param {Array} array - The array to test.
   * @returns {boolean} - True if none of the elements satisfy the predicate, otherwise false.
   * 
   * @example
   * const isEven = num => num % 2 === 0;
   * let numbers = [1, 3, 5, 7];
   * console.log(none(isEven, numbers)); // true
   * 
   * let mixedNumbers = [1, 2, 3, 5];
   * console.log(none(isEven, mixedNumbers)); // false
   */
  export const none = (predicate, array) =>
    array.reduce((acc, value) => acc && !predicate(value), true);
  
  /**
   * Checks if all elements in the array satisfy the provided predicate function.
   * 
   * @param {Function} predicate - The function to test each element.
   * @param {Array} array - The array to test.
   * @returns {boolean} - True if all elements satisfy the predicate, otherwise false.
   * 
   * @example
   * const isEven = num => num % 2 === 0;
   * let numbers = [2, 4, 6, 8];
   * console.log(all(isEven, numbers)); // true
   * 
   * let mixedNumbers = [2, 4, 5, 8];
   * console.log(all(isEven, mixedNumbers)); // false
   */
  export const all = (predicate, array) =>
    array.reduce((acc, value) => acc && predicate(value), true);
  
  /**
   * Extracts the values of a specified property from an array of objects.
   * 
   * @param {string} key - The property name to pluck.
   * @param {Array} array - The array of objects to pluck from.
   * @returns {Array} - An array of values for the specified property.
   * 
   * @example
   * const users = [
   *   { id: 1, name: 'Alice' },
   *   { id: 2, name: 'Bob' },
   *   { id: 3, name: 'Charlie' }
   * ];
   * console.log(pluck('name', users)); // ['Alice', 'Bob', 'Charlie']
   */
  export const pluck = (key, array) =>
    array.reduce((values, current) => {
      values.push(current[key]);
      return values;
    }, []);
  
  /**
  * Applies a reducer function to each element of an array and returns an array of accumulated results.
  * 
  * @param {Function} reducer - The reducer function that takes accumulator and current value.
  * @param {*} initialValue - The initial value of the accumulator.
  * @param {Array} array - The array to scan.
  * @returns {Array} - An array of accumulated values after applying the reducer to each element.
  * 
  * @example
  * const add = (acc, value) => acc + value;
  * const numbers = [1, 2, 3, 4, 5];
  * console.log(scan(add, 0, numbers)); // [1, 3, 6, 10, 15]
  */
  export const scan = (reducer, initialValue, array) => {
    const reducedValues = [];
    array.reduce((acc, current) => {
      const newAcc = reducer(acc, current);
      reducedValues.push(newAcc);
      return newAcc;
    }, initialValue);
  
    return reducedValues;
  };
  
  /**
   * Chunks an array into smaller arrays of a specified size.
   * 
   * @param {Array} arr - The array to chunk.
   * @param {number} size - The size of each chunk.
   * @returns {Array} - An array of smaller arrays (chunks).
   * 
   * @example
   * const numbers = [1, 2, 3, 4, 5, 6, 7, 8, 9];
   * console.log(chunk(numbers, 3)); // [[1, 2, 3], [4, 5, 6], [7, 8, 9]]
   */
  export const chunk = (arr, size) =>
    Array.from({ length: Math.ceil(arr.length / size) }, (v, i) =>
      arr.slice(i * size, i * size + size)
    );
  
  /**
   * Checks if at least one element in the array satisfies the provided predicate function.
   * 
   * @param {Function} predicate - The function to test each element.
   * @param {Array} array - The array to test.
   * @returns {boolean} - True if at least one element satisfies the predicate, otherwise false.
   * 
   * @example
   * const isEven = num => num % 2 === 0;
   * let numbers = [1, 3, 5, 7, 8];
   * console.log(some(isEven, numbers)); // true
   */
  export const some = (predicate, array) =>
    array.reduce((acc, value) => acc || predicate(value), false);
  
  /**
   * Partitions an array into two arrays based on a predicate function.
   * 
   * @param {Function} predicate - The function to test each element.
   * @param {Array} array - The array to partition.
   * @returns {Array} - An array with two sub arrays: the first containing elements that satisfy the predicate, and the second containing the rest.
   * 
   * @example
   * const isEven = num => num % 2 === 0;
   * let numbers = [1, 2, 3, 4, 5];
   * console.log(partition(isEven, numbers)); // [[2, 4], [1, 3, 5]]
   */
  export const partition = (predicate, array) =>
    array.reduce(
      (result, item) => {
        const [list1, list2] = result;
  
        if (predicate(item)) {
          list1.push(item);
        } else {
          list2.push(item);
        }
  
        return result;
      },
      [[], []]
    );
  
  /**
   * Filters out elements from the array that satisfy the provided predicate function.
   * 
   * @param {Function} predicate - The function to test each element.
   * @param {Array} array - The array to filter.
   * @returns {Array} - A new array with elements that do not satisfy the predicate.
   * 
   * @example
   * const isEven = num => num % 2 === 0;
   * let numbers = [1, 2, 3, 4, 5];
   * console.log(reject(isEven, numbers)); // [1, 3, 5]
   */
  export const reject = (predicate, array) =>
    array.reduce((newArray, item) => {
      if (!predicate(item)) {
        newArray.push(item);
      }
      return newArray;
    }, []);
  
  /**
   * Calls a given function a specified number of times.
   * 
   * @param {Function} func - The function to be called.
   * @param {number} n - The number of times to call the function.
   * 
   * @example
   * const sayHello = () => console.log('Hello');
   * times(sayHello, 3);
   * // Output:
   * // Hello
   * // Hello
   * // Hello
   */
  export const times = (func, n) => {
    Array.from(Array(n)).forEach(() => {
      func();
    });
  };
  
  /**
   * Finds an object in an array by a specific property value.
   * 
   * @param {Array} array - The array of objects to search.
   * @param {string} propertyName - The property name to match.
   * @param {*} value - The value to match against the property.
   * @returns {*} - The first object found matching the criteria, or undefined if not found.
   * 
   * @example
   * let users = [
   *   { id: 1, name: 'Alice' },
   *   { id: 2, name: 'Bob' },
   *   { id: 3, name: 'Charlie' }
   * ];
   * let user = findByProperty(users, 'id', 2);
   * console.log(user); // { id: 2, name: 'Bob' }
   */
  export function findByProperty(array, propertyName, value) {
    return array.find(item => item[propertyName] === value);
  }
  
  /**
   * Removes duplicate elements from an array.
   * 
   * @param {Array} array - The array from which to remove duplicates.
   * @returns {Array} - A new array with unique elements.
   * 
   * @example
   * let numbers = [1, 2, 2, 3, 4, 4, 5];
   * let uniqueNumbers = removeDuplicates(numbers);
   * console.log(uniqueNumbers); // [1, 2, 3, 4, 5]
   */
  export function removeDuplicates(array) {
    return array.filter((value, index, self) => self.indexOf(value) === index);
  }
  
  /**
   * Removes duplicate objects from an array based on a specific property value.
   * 
   * @param {Array} array - The array of objects to remove duplicates from.
   * @param {string} propertyName - The property name to check for uniqueness.
   * @returns {Array} - A new array with unique objects based on the property value.
   * 
   * @example
   * let users = [
   *   { id: 1, name: 'Alice' },
   *   { id: 2, name: 'Bob' },
   *   { id: 1, name: 'Alice' } // Duplicate
   * ];
   * let uniqueUsers = removeDuplicatesByProperty(users, 'id');
   * console.log(uniqueUsers);
   * // [
   * //   { id: 1, name: 'Alice' },
   * //   { id: 2, name: 'Bob' }
   * // ]
   */
  export function removeDuplicatesByProperty(array, propertyName) {
    let seen = new Set();
    return array.filter(item => {
      let propertyValue = item[propertyName];
      return seen.has(propertyValue) ? false : seen.add(propertyValue);
    });
  }
  
  /**
   * Groups objects in an array by a specific property.
   * 
   * @param {Array} array - The array of objects to group.
   * @param {string} propertyName - The property name to group by.
   * @returns {Object} - An object where keys are unique property values and values are arrays of objects.
   * 
   * @example
   * let products = [
   *   { id: 1, category: 'Electronics', name: 'Laptop' },
   *   { id: 2, category: 'Electronics', name: 'Phone' },
   *   { id: 3, category: 'Clothing', name: 'Shirt' },
   *   { id: 4, category: 'Clothing', name: 'Pants' }
   * ];
   * let groupedProducts = groupByProperty(products, 'category');
   * console.log(groupedProducts);
   * // {
   * //   Electronics: [
   * //     { id: 1, category: 'Electronics', name: 'Laptop' },
   * //     { id: 2, category: 'Electronics', name: 'Phone' }
   * //   ],
   * //   Clothing: [
   * //     { id: 3, category: 'Clothing', name: 'Shirt' },
   * //     { id: 4, category: 'Clothing', name: 'Pants' }
   * //   ]
   * // }
   */
  export function groupByProperty(array, propertyName) {
    return array.reduce((groups, item) => {
      const key = item[propertyName];
      groups[key] = groups[key] || [];
      groups[key].push(item);
      return groups;
    }, {});
  }
  
  /**
   * Flattens an array of arrays into a single array.
   * 
   * @param {Array} arrayOfArrays - The array of arrays to flatten.
   * @returns {Array} - A new flattened array.
   * 
   * @example
   * let arrays = [[1, 2], [3, 4], [5, 6]];
   * let flattened = flattenArray(arrays);
   * console.log(flattened); // [1, 2, 3, 4, 5, 6]
   */
  export function flattenArray(arrayOfArrays) {
    return arrayOfArrays.reduce((flat, current) => flat.concat(current), []);
  }
  
  /**
   * Randomly shuffles the elements of an array.
   * 
   * @param {Array} array - The array to shuffle.
   * @returns {Array} - A new shuffled array.
   * 
   * @example
   * let cards = ['Ace', 'King', 'Queen', 'Jack'];
   * let shuffledCards = shuffleArray(cards);
   * console.log(shuffledCards); // Randomly shuffled array
   */
  export function shuffleArray(array) {
    for (let i = array.length - 1; i > 0; i--) {
      const j = Math.floor(Math.random() * (i + 1));
      [array[i], array[j]] = [array[j], array[i]];
    }
    return array;
  }
  
  /**
   * Deep merges two objects.
   * 
   * @param {Object} target - The target object to merge into.
   * @param {Object} source - The source object to merge from.
   * @returns {Object} - The merged object.
   * 
   * @example
   * const obj1 = { a: 1, b: { c: 2 } };
   * const obj2 = { b: { d: 3 }, e: 4 };
   * console.log(deepMerge(obj1, obj2)); // { a: 1, b: { c: 2, d: 3 }, e: 4 }
   */
  export const deepMerge = (target, source) => {
    for (const key in source) {
      if (source[key] instanceof Object) {
        Object.assign(source[key], deepMerge(target[key], source[key]));
      }
    }
    Object.assign(target || {}, source);
    return target;
  };
  
  /**
   * Filters an object by its keys.
   * 
   * @param {Object} obj - The object to filter.
   * @param {Array} keys - The array of keys to include.
   * @returns {Object} - A new object filtered by the specified keys.
   * 
   * @example
   * const obj = { a: 1, b: 2, c: 3 };
   * const filtered = filterByKeys(obj, ['a', 'c']);
   * console.log(filtered); // { a: 1, c: 3 }
   */
  export const filterByKeys = (obj, keys) =>
    keys.reduce((acc, key) => {
      if (obj.hasOwnProperty(key)) {
        acc[key] = obj[key];
      }
      return acc;
    }, {});
  
  /**
  * Flattens a nested object into a flat object with dot-separated keys.
  * 
  * @param {Object} obj - The object to flatten.
  * @param {string} prefix - The current key prefix (used internally).
  * @returns {Object} - The flattened object.
  * 
  * @example
  * const obj = { a: { b: { c: 42 } }, d: { e: 55 } };
  * console.log(flattenObject(obj)); // { 'a.b.c': 42, 'd.e': 55 }
  */
  export const flattenObject = (obj, prefix = '') =>
    Object.keys(obj).reduce((acc, k) => {
      const pre = prefix.length ? `${prefix}.` : '';
      if (typeof obj[k] === 'object' && obj[k] !== null && !Array.isArray(obj[k])) {
        Object.assign(acc, flattenObject(obj[k], pre + k));
      } else {
        acc[pre + k] = obj[k];
      }
      return acc;
    }, {});
  
  /**
   * Extracts a nested property from an object using a dot-separated key string.
   * 
   * @param {string} key - The dot-separated key string (e.g., 'a.b.c').
   * @returns {Function} - A function that takes an object and returns the value at the specified key.
   * 
   * @example
   * const obj = { a: { b: { c: 42 } } };
   * const getValue = pluckDeep('a.b.c');
   * console.log(getValue(obj)); // 42
   */
  export const pluckDeep = key => obj => key.split('.').reduce((acm, key) => acm[key], obj);
  
  /**
   * Composes multiple functions into a single function.
   * 
   * @param  {...Function} fns - The functions to compose.
   * @returns {Function} - A function that takes an initial value and applies each function from right to left.
   * 
   * @example
   * const addOne = x => x + 1;
   * const double = x => x * 2;
   * const addOneAndDouble = compose(double, addOne);
   * console.log(addOneAndDouble(2)); // 6 (2 + 1 = 3, 3 * 2 = 6)
   */
  export const compose = (...fns) => res => fns.reduce((acm, next) => next(acm), res);
  
  /**
   * Generates a list by repeatedly applying a function to a seed value.
   * 
   * @param {Function} f - The function to apply. Should return a pair [value, nextSeed] or null.
   * @param {*} seed - The initial seed value.
   * @returns {Array} - The list of generated values.
   * 
   * @example
   * const f = n => n > 0 ? [n, n - 1] : null;
   * const result = unfold(f, 5);
   * console.log(result); // [5, 4, 3, 2, 1]
   */
  export const unfold = (f, seed) => {
    const go = (f, seed, acc) => {
      const res = f(seed);
      return res ? go(f, res[1], acc.concat([res[0]])) : acc;
    };
    return go(f, seed, []);
  };
  
  /**
   * Applies a function to each element in an array.
   * 
   * @param {Function} fn - The function to apply to each element.
   * @returns {Function} - A function that takes an array and returns a new array with the function applied to each element.
   * 
   * @example
   * const double = x => x * 2;
   * const doubleArray = map(double);
   * console.log(doubleArray([1, 2, 3])); // [2, 4, 6]
   */
  export const map = fn => arr => arr.map(fn);
  
  /**
   * Filters elements in an array based on a predicate function.
   * 
   * @param {Function} predicate - The function to test each element.
   * @returns {Function} - A function that takes an array and returns a new array with elements that pass the test.
   * 
   * @example
   * const isEven = x => x % 2 === 0;
   * const filterEven = filter(isEven);
   * console.log(filterEven([1, 2, 3, 4])); // [2, 4]
   */
  export const filter = predicate => arr => arr.filter(predicate);
  
  /**
   * Reduces an array to a single value by applying a function to each element and accumulating the result.
   * 
   * @param {Function} fn - The function to apply to each element and the accumulator.
   * @param {*} initialValue - The initial value for the accumulator.
   * @returns {Function} - A function that takes an array and returns the accumulated result.
   * 
   * @example
   * const sum = (acc, x) => acc + x;
   * const sumArray = reduce(sum, 0);
   * console.log(sumArray([1, 2, 3, 4])); // 10
   */
  export const reduce = (fn, initialValue) => arr => arr.reduce(fn, initialValue);
  
  /**
   * Maps each element using a mapping function, then flattens the result into a new array.
   * 
   * @param {Function} fn - The function to map each element.
   * @returns {Function} - A function that takes an array and returns a new array that is the result of applying the function and flattening the result.
   * 
   * @example
   * const duplicate = x => [x, x];
   * const duplicateArray = flatMap(duplicate);
   * console.log(duplicateArray([1, 2, 3])); // [1, 1, 2, 2, 3, 3]
   */
  export const flatMap = fn => arr => arr.flatMap(fn);
  
  /**
   * Creates a pipeline of functions to apply from left to right.
   * 
   * @param  {...Function} fns - The functions to apply.
   * @returns {Function} - A function that takes an initial value and applies each function from left to right.
   * 
   * @example
   * const addOne = x => x + 1;
   * const double = x => x * 2;
   * const addOneThenDouble = pipe(addOne, double);
   * console.log(addOneThenDouble(2)); // 6 (2 + 1 = 3, 3 * 2 = 6)
   */
  export const pipe = (...fns) => res => fns.reduce((acm, next) => next(acm), res);
  
  /**
   * Transforms a function so that it can be called with partial arguments.
   * 
   * @param {Function} fn - The function to curry.
   * @returns {Function} - A curried version of the original function.
   * 
   * @example
   * const add = (a, b) => a + b;
   * const curriedAdd = curry(add);
   * console.log(curriedAdd(1)(2)); // 3
   */
  export const curry = fn => {
    const curried = (...args) =>
      args.length >= fn.length ? fn(...args) : (...next) => curried(...args, ...next);
    return curried;
  };
  
  // A utility function to debounce another function by a specified delay
  export const debounce = (fn, delay) => {
    let timeout = -1; // Initialize timeout ID
    return (...args) => {
      if (timeout !== -1) {
        clearTimeout(timeout); // Clear the existing timeout if any
      }
      // @ts-ignore
      timeout = setTimeout(fn, delay, ...args); // Set a new timeout
    };
  };