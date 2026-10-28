"""
Sample code snippets and demo payloads for CodeXplain Hub.
Provides instant test cases for users to explore the application without manual typing.
"""

SAMPLE_SNIPPETS = {
    "Java: Student Constructor & Execution Path": {
        "language": "java",
        "title": "Java Constructor Jump, Heap Allocation & Output",
        "code": '''class Student {
    int id;

    Student(int id) {
        this.id = id;
    }

    void display() {
        System.out.println(this.id);
    }

    public static void main(String[] args) {
        Student s = new Student(101);
        s.display();
    }
}
'''
    },
    "Java: Scope Keywords ('this' & 'super')": {
        "language": "java",
        "title": "Java Inheritance & Scope Simulation with 'this' and 'super'",
        "code": '''// Parent Superclass
class Vehicle {
    protected String brand;
    protected int speed;

    public Vehicle(String brand, int speed) {
        this.brand = brand;      // 'this.brand' binds to Vehicle instance field
        this.speed = speed;      // 'this.speed' resolves local parameter shadowing
    }

    public void displaySpecs() {
        System.out.println("Vehicle brand: " + this.brand + ", speed: " + this.speed);
    }
}

// Derived Subclass with Shadowed Field and Keyword Resolution
class ElectricCar extends Vehicle {
    private int batteryCapacity;
    private int speed; // Shadowing parent field!

    public ElectricCar(String brand, int speed, int batteryCapacity) {
        super(brand, 60);         // 'super(...)' calls Vehicle superclass constructor
        this.speed = speed;       // 'this.speed' writes to ElectricCar's own field
        this.batteryCapacity = batteryCapacity;
    }

    @Override
    public void displaySpecs() {
        super.displaySpecs();     // 'super.displaySpecs()' calls parent method implementation
        System.out.println("ElectricCar speed: " + this.speed);    // 'this' accesses subclass speed
        System.out.println("Parent Vehicle speed: " + super.speed); // 'super' accesses parent speed
        System.out.println("Battery: " + this.batteryCapacity + " kWh");
    }
}
'''
    },
    "Python: Buggy Binary Search (Logic Flaw)": {
        "language": "python",
        "title": "Buggy Binary Search with Off-by-One Flaw",
        "code": '''def binary_search(arr, target):
    """
    Search for target in sorted list arr.
    Returns index if found, else -1.
    """
    left = 0
    right = len(arr)  # Bug: Off-by-one! Should be len(arr) - 1
    
    while left < right:  # Potential infinite loop or missed target when left == right
        mid = (left + right) // 2
        
        if arr[mid] == target:
            return mid
        elif arr[mid] < target:
            left = mid  # Bug: Should be mid + 1 to avoid infinite loop
        else:
            right = mid - 1
            
    return -1

# Test driver
numbers = [2, 5, 8, 12, 16, 23, 38, 56, 72, 91]
print("Found 23 at index:", binary_search(numbers, 23))
print("Found 91 at index:", binary_search(numbers, 91))
'''
    },
    "JavaScript: Async Batch Processor with Retries": {
        "language": "javascript",
        "title": "Async Batch Processor with Exponential Backoff",
        "code": '''/**
 * Processes items in parallel batches with retry backoff.
 */
async function processBatchWithRetry(items, processFn, batchSize = 3, maxRetries = 2) {
    const results = [];
    
    for (let i = 0; i < items.length; i += batchSize) {
        const batch = items.slice(i, i + batchSize);
        const batchPromises = batch.map(async (item) => {
            let attempts = 0;
            while (attempts <= maxRetries) {
                try {
                    return await processFn(item);
                } catch (err) {
                    attempts++;
                    if (attempts > maxRetries) throw err;
                    const delay = Math.pow(2, attempts) * 100;
                    await new Promise(r => setTimeout(r, delay));
                }
            }
        });
        
        const batchResults = await Promise.allSettled(batchPromises);
        results.push(...batchResults);
    }
    
    return results;
}
'''
    },
    "C++: QuickSort with In-Place Partitioning": {
        "language": "cpp",
        "title": "QuickSort with Lomuto Partition Scheme",
        "code": '''#include <iostream>
#include <vector>
#include <algorithm>

int partition(std::vector<int>& arr, int low, int high) {
    int pivot = arr[high];
    int i = low - 1;
    
    for (int j = low; j < high; ++j) {
        if (arr[j] <= pivot) {
            ++i;
            std::swap(arr[i], arr[j]);
        }
    }
    std::swap(arr[i + 1], arr[high]);
    return i + 1;
}

void quickSort(std::vector<int>& arr, int low, int high) {
    if (low < high) {
        int pi = partition(arr, low, high);
        quickSort(arr, low, pi - 1);
        quickSort(arr, pi + 1, high);
    }
}
'''
    }
}

# Pre-computed rich demo analysis for Java Scope Keywords
DEMO_JAVA_ANALYSIS = {
    "functional_overview": {
        "summary": "This module illustrates Object-Oriented Inheritance, Constructor Chaining, and Variable Shadowing in Java. It models a Vehicle superclass and an ElectricCar subclass, explicitly demonstrating how the 'this' keyword disambiguates current instance fields while the 'super' keyword accesses the parent class state and behavior.",
        "capabilities": [
            "Demonstrates constructor chaining using `super(...)` to initialize parent class invariants.",
            "Resolves field shadowing between method parameters and instance variables using `this`.",
            "Illustrates method overriding and superclass invocation via `super.displaySpecs()`.",
            "Demonstrates direct access to parent state (`super.speed`) versus subclass state (`this.speed`)."
        ],
        "inputs": [
            {"param": "brand", "type": "String", "description": "Manufacturer brand name passed to constructor."},
            {"param": "speed", "type": "int", "description": "Subclass velocity value which shadows parent speed."},
            {"param": "batteryCapacity", "type": "int", "description": "Battery capacity in kWh specific to ElectricCar."}
        ],
        "outputs": {
            "type": "void",
            "description": "Prints vehicle specifications to standard output."
        },
        "mermaid": """graph TD
    subgraph HeapMemory["📦 Heap Memory Simulation"]
        CarInstance["ElectricCar Instance (@0x7F2A)\\n- batteryCapacity: 75\\n- speed (child): 120"]
        ParentVehicle["Vehicle Superclass Frame (@0x1A04)\\n- brand: Tesla\\n- speed (parent): 60"]
    end

    Caller["Program Entry Point"] -->|new ElectricCar(...)| CarInstance
    CarInstance -- "super(brand, 60)" -->|Delegates to| ParentVehicle
    CarInstance -- "this.speed = 120" -->|Writes to| CarInstance
    CarInstance -- "super.speed" -->|Reads from| ParentVehicle"""
    },
    "line_breakdown": [
        {
            "line_range": "Lines 6-9",
            "code": "public Vehicle(String brand, int speed) {\\n    this.brand = brand;\\n    this.speed = speed;\\n}",
            "explanation": "Parent constructor. The parameters 'brand' and 'speed' shadow the class fields. 'this.brand' explicitly addresses the heap object's instance variable, avoiding parameter ambiguity."
        },
        {
            "line_range": "Lines 20-24",
            "code": "public ElectricCar(String brand, int speed, int batteryCapacity) {\\n    super(brand, 60);\\n    this.speed = speed;\\n    this.batteryCapacity = batteryCapacity;\\n}",
            "explanation": "'super(brand, 60)' must be the very first statement. It delegates to Vehicle's constructor. Then 'this.speed = speed' sets the ElectricCar's shadowed speed field."
        },
        {
            "line_range": "Lines 28-32",
            "code": "super.displaySpecs();\\nSystem.out.println(\"ElectricCar speed: \" + this.speed);\\nSystem.out.println(\"Parent Vehicle speed: \" + super.speed);",
            "explanation": "Execution trace: 'super.displaySpecs()' prints the parent's brand and parent's speed (60). Then 'this.speed' accesses the subclass speed (120), whereas 'super.speed' accesses the parent's shadowed speed (60)."
        }
    ],
    "debugger": {
        "status": "Clean / Design Advisory",
        "summary": "Code runs cleanly without syntax errors. However, field shadowing ('speed' defined in both child and parent) is an OOP anti-pattern that can cause developer confusion.",
        "issues": [
            {
                "severity": "Warning",
                "title": "Field Shadowing on 'speed'",
                "description": "ElectricCar declares a field named 'speed' that hides 'Vehicle.speed'. In production code, field hiding should be avoided; use different names or accessor methods.",
                "fix": "Remove the redundant 'speed' declaration in ElectricCar or use getter/setter encapsulation."
            }
        ],
        "corrected_code": '''class Vehicle {
    protected String brand;
    protected int speed;

    public Vehicle(String brand, int speed) {
        this.brand = brand;
        this.speed = speed;
    }

    public void displaySpecs() {
        System.out.println("Brand: " + this.brand + " | Speed: " + this.speed);
    }
}

class ElectricCar extends Vehicle {
    private int batteryCapacity;

    public ElectricCar(String brand, int speed, int batteryCapacity) {
        super(brand, speed); // Clean reuse without shadowing
        this.batteryCapacity = batteryCapacity;
    }

    @Override
    public void displaySpecs() {
        super.displaySpecs();
        System.out.println("Battery: " + this.batteryCapacity + " kWh");
    }
}
'''
    },
    "complexity": {
        "score": 2,
        "badge": "Low Complexity",
        "badge_color": "#10b981",
        "time_complexity": "O(1)",
        "space_complexity": "O(1)",
        "cyclomatic_complexity": "1 (Sequential initialization and dispatch)",
        "bottlenecks": "No computational overhead. Standard JVM virtual method table dispatch.",
        "architecture_critique": "Standard single-inheritance hierarchy with constructor delegation. Encapsulation could be improved by making fields private and exposing getters."
    },
    "translations": {
        "python": '''class Vehicle:
    def __init__(self, brand: str, speed: int):
        self.brand = brand        # Equivalent to this.brand
        self.speed = speed

    def display_specs(self):
        print(f"Brand: {self.brand} | Speed: {self.speed}")

class ElectricCar(Vehicle):
    def __init__(self, brand: str, speed: int, battery_capacity: int):
        super().__init__(brand, 60)   # Equivalent to super(brand, 60)
        self.speed = speed            # Overrides/replaces speed attribute
        self.battery_capacity = battery_capacity

    def display_specs(self):
        super().display_specs()       # Calls Vehicle's display_specs()
        print(f"ElectricCar speed: {self.speed}")
        print(f"Battery: {self.battery_capacity} kWh")
''',
        "cpp": '''#include <iostream>
#include <string>

class Vehicle {
protected:
    std::string brand;
    int speed;

public:
    Vehicle(std::string brand, int speed) : brand(brand), speed(speed) {}

    virtual void displaySpecs() const {
        std::cout << "Brand: " << this->brand << " | Speed: " << this->speed << std::endl;
    }
};

class ElectricCar : public Vehicle {
private:
    int batteryCapacity;
    int speed; // Shadowing field

public:
    ElectricCar(std::string brand, int speed, int battery)
        : Vehicle(brand, 60), batteryCapacity(battery), speed(speed) {}

    void displaySpecs() const override {
        Vehicle::displaySpecs(); // Equivalent to super.displaySpecs()
        std::cout << "ElectricCar speed: " << this->speed << std::endl;
        std::cout << "Parent Vehicle speed: " << Vehicle::speed << std::endl;
        std::cout << "Battery: " << this->batteryCapacity << " kWh" << std::endl;
    }
};
'''
    }
}

# Pre-computed rich demo analysis for Python Buggy Binary Search
DEMO_ANALYSIS = {
    "functional_overview": {
        "summary": "This module provides a classic search routine designed to locate a specific target element within an ordered sequence in logarithmic time. However, due to critical boundary and indexing errors, the current implementation fails to find elements at the end of the collection and can enter an infinite loop when the target lies in the upper sub-array.",
        "capabilities": [
            "Accepts a pre-sorted integer array and a query target value.",
            "Divides the search interval in half on each iteration using midpoint calculation.",
            "Aims to achieve O(log n) average and worst-case time complexity.",
            "Designed to return the integer 0-indexed position or -1 if the target is absent."
        ],
        "inputs": [
            {"param": "arr", "type": "List[int]", "description": "Strictly ascending sorted array of elements to search within."},
            {"param": "target", "type": "int", "description": "The specific value to locate within the array."}
        ],
        "outputs": {
            "type": "int",
            "description": "Zero-based index of target if found; -1 if the target does not exist in arr."
        },
        "mermaid": """graph TD
    A[Start: binary_search] --> B[Initialize left = 0, right = len(arr)]
    B --> C{left <= right?}
    C -- Yes --> D[Compute mid = (left + right) // 2]
    D --> E{arr[mid] == target?}
    E -- Yes --> F[Return mid: Found]
    E -- No --> G{arr[mid] < target?}
    G -- Yes --> H[left = mid + 1]
    G -- No --> I[right = mid - 1]
    H --> C
    I --> C
    C -- No --> J[Return -1: Not Found]"""
    },
    "line_breakdown": [
        {
            "line_range": "Lines 1-5",
            "code": "def binary_search(arr, target):\\n    left = 0\\n    right = len(arr)",
            "explanation": "Defines the search signature and initializes two tracking pointers. Notice that `right` is set to `len(arr)` instead of `len(arr) - 1`, making `arr[right]` an invalid out-of-bounds index if accessed directly."
        },
        {
            "line_range": "Lines 7-8",
            "code": "while left < right:\\n    mid = (left + right) // 2",
            "explanation": "Loops while the window has positive width. Using `<` rather than `<=` causes the algorithm to terminate prematurely without checking the final remaining element when `left == right`."
        },
        {
            "line_range": "Lines 10-11",
            "code": "if arr[mid] == target:\\n    return mid",
            "explanation": "Examines the element at the midpoint index. If an exact match is discovered, execution immediately halts and yields the matching index."
        },
        {
            "line_range": "Lines 12-13",
            "code": "elif arr[mid] < target:\\n    left = mid",
            "explanation": "CRITICAL FLAW: Assigns `left = mid` instead of `left = mid + 1`. When `right - left == 1` and `arr[mid] < target`, `mid` evaluates to `left`, causing `left` to remain unchanged and trapping the algorithm in an infinite loop."
        },
        {
            "line_range": "Lines 14-17",
            "code": "else:\\n    right = mid - 1\\nreturn -1",
            "explanation": "Narrows the search window to the left partition by setting `right = mid - 1`. If the loop finishes without finding the target, the function falls through and returns `-1`."
        }
    ],
    "debugger": {
        "status": "Errors Detected",
        "summary": "2 Critical Logic Flaws & 1 Boundary Error found that prevent proper convergence and cause infinite loops.",
        "issues": [
            {
                "severity": "Critical",
                "title": "Infinite Loop in Right Partitioning",
                "description": "Setting `left = mid` when integer division rounds down `(left + right) // 2` leads to `mid == left`. The search space never shrinks, freezing the thread indefinitely.",
                "fix": "Change to `left = mid + 1`."
            },
            {
                "severity": "Critical",
                "title": "Premature Loop Termination (Missed Target)",
                "description": "The loop predicate `while left < right:` terminates when `left == right`. If the target element resides precisely at that index, it is skipped entirely.",
                "fix": "Change condition to `while left <= right:` and set initial `right = len(arr) - 1`."
            },
            {
                "severity": "Warning",
                "title": "Initial Boundary Off-By-One",
                "description": "`right = len(arr)` points past the end of the 0-indexed array.",
                "fix": "Initialize `right = len(arr) - 1`."
            }
        ],
        "corrected_code": '''def binary_search(arr, target):
    """
    Search for target in sorted list arr.
    Returns index if found, else -1.
    """
    left = 0
    right = len(arr) - 1  # Corrected: standard inclusive right boundary
    
    while left <= right:  # Corrected: checks when single element remains
        mid = (left + right) // 2
        
        if arr[mid] == target:
            return mid
        elif arr[mid] < target:
            left = mid + 1  # Corrected: advance pointer to eliminate mid
        else:
            right = mid - 1  # Contract right boundary
            
    return -1

# Test driver
numbers = [2, 5, 8, 12, 16, 23, 38, 56, 72, 91]
print("Found 23 at index:", binary_search(numbers, 23))  # 5
print("Found 91 at index:", binary_search(numbers, 91))  # 9
print("Target 100:", binary_search(numbers, 100))        # -1
'''
    },
    "complexity": {
        "score": 3,
        "badge": "Low Complexity",
        "badge_color": "#10b981",
        "time_complexity": "O(log n)",
        "space_complexity": "O(1)",
        "cyclomatic_complexity": "3 (Low branching depth)",
        "bottlenecks": "No computational bottlenecks. The search halving guarantees logarithmic runtime. In languages without arbitrary precision integers, potential integer overflow on `(left + right)` can be avoided with `left + (right - left) // 2`.",
        "architecture_critique": "The function adheres to clean single-responsibility principles. It operates in place with zero memory allocations beyond pointer variables. It provides an optimal template once boundary invariants are rectified."
    },
    "translations": {
        "javascript": '''/**
 * Binary search implementation in JavaScript (ES6+).
 * @param {number[]} arr - Sorted array of numbers
 * @param {number} target - Value to search for
 * @returns {number} Index if found, otherwise -1
 */
function binarySearch(arr, target) {
    let left = 0;
    let right = arr.length - 1;
    
    while (left <= right) {
        const mid = left + Math.floor((right - left) / 2);
        
        if (arr[mid] === target) {
            return mid;
        } else if (arr[mid] < target) {
            left = mid + 1;
        } else {
            right = mid - 1;
        }
    }
    
    return -1;
}
''',
        "cpp": '''#include <iostream>
#include <vector>

int binarySearch(const std::vector<int>& arr, int target) {
    int left = 0;
    int right = static_cast<int>(arr.size()) - 1;
    
    while (left <= right) {
        int mid = left + (right - left) / 2;
        if (arr[mid] == target) {
            return mid;
        } else if (arr[mid] < target) {
            left = mid + 1;
        } else {
            right = mid - 1;
        }
    }
    return -1;
}
'''
    }
}
