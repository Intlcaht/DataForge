import { useRef } from 'react';
import { useVirtualizer } from '@tanstack/react-virtual';


// // Example usage component to demonstrate how to use the VirtualizedList
// function VirtualizedListExample() {
//   // Create an array of 10,000 items for demonstration
//   const items = Array.from({ length: 10000 }, (_, i) => ({
//     id: i,
//     text: `Item ${i}`,
//   }));

//   return (
//     <div className="p-4 max-w-md mx-auto bg-gray-100 rounded-lg">
//       <h2 className="text-xl font-bold mb-4">Virtualized List Demo</h2>
//       <VirtualizedList
//         items={items}
//         height={400}
//         width={100}
//         renderItem={(item) => (
//           <div  className="p-4 border-b border-gray-200 bg-white hover:bg-gray-50">
//             {item.text}
//           </div>
//         )}
//       />
//     </div>
//   );
// }

// // Return the example component to show how it works
// export { VirtualizedListExample };

// Define the props for our VirtualizedList component
type VirtualizedListProps<T> = {
  // items array, contains the list data to be displayed
  items: T[];
  // height of the virtualized list container
  height: number;
  // width of the virtualized list container
  width: number;
  // height of each item (optional, defaults to 50)
  itemHeight?: number;
  // renderItem is a function to render each item in the list
  renderItem: (item: T, index: number) => React.ReactNode;
};

export default function VirtualizedList<T>({
  items,
  height,
  width,
  itemHeight = 50,
  renderItem,
}: VirtualizedListProps<T>) {
  // Create a reference to the parent container, used for scroll detection
  const parentRef = useRef<HTMLDivElement>(null);

  // Set up the virtualizer from '@tanstack/react-virtual'
  const virtualizer = useVirtualizer({
    // count refers to the total number of items in the list
    count: items.length,
    // getScrollElement provides the scroll container, which is the parentRef
    getScrollElement: () => parentRef.current,
    // estimateSize gives the height of each item in the list (default is 'itemHeight')
    estimateSize: () => itemHeight,
  });

  return (
    <div
      // Assign the parent reference to the scroll container
      ref={parentRef}
      // Ensures the container can scroll
      className="overflow-auto"
      style={{
        height,  // Set the height of the virtualized list container
        width,   // Set the width of the virtualized list container
      }}
    >
      {/* This div ensures proper scrolling with the virtual items */}
      <div
        className="relative w-full"
        // Set the total height of the virtualized content based on the total size of items
        style={{
          height: `${virtualizer.getTotalSize()}px`,
        }}
      >
        {/* Loop through the virtual items generated by the virtualizer */}
        {virtualizer.getVirtualItems().map((virtualItem) => (
          <div
            key={virtualItem.key}  // Use the virtual item's key for React reconciliation
            className="absolute top-0 left-0 w-full"
            style={{
              // Set the height of each item (may vary due to dynamic size)
              height: `${virtualItem.size}px`,
              // Adjust the item's position on the y-axis based on its starting point
              transform: `translateY(${virtualItem.start}px)`,
            }}
          >
            {/* Render the actual content for this item using the provided renderItem function */}
            {renderItem(items[virtualItem.index], virtualItem.index)}
          </div>
        ))}
      </div>
    </div>
  );
}
