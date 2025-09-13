#!/usr/bin/env python3
"""
SimpleCOL Usage Examples

This file demonstrates various features of SimpleCOL for formatting tabular data.
Run with: python examples.py
"""

import io
from simplecol import Model, Table, Screen, Alignment, Column


def example_1_from_rows():
    """Example 1: Creating model from row data"""
    print("=== Example 1: From Rows ===")
    
    rows = [
        ["Name", "Age", "City"],
        ["Alice", "25", "New York"],
        ["Bob", "30", "San Francisco"],
        ["Charlie", "35", "Chicago"]
    ]
    
    # Without headers
    model = Model.from_rows(rows)
    print("Without headers:")
    print(Screen(model))
    print()
    
    # With headers
    model = Model.from_rows(rows, headers=True)
    print("With headers:")
    print(Table(model))
    print()


def example_2_auto_alignment():
    """Example 2: Automatic alignment detection"""
    print("=== Example 2: Auto Alignment ===")
    
    data = [
        ["Product", "Price", "Quantity", "Code"],
        ["Widget", "12.99", "150", "W001"],
        ["Gadget", "5.25", "75", "G002"],
        ["Tool", "25.00", "200", "T003"]
    ]
    
    # Let SimpleCOL auto-detect alignment per column
    model = Model.from_rows(data, headers=True, align=None)
    print("Auto-detected alignments:")
    print(Table(model))
    
    # Show what was detected
    for i, col in enumerate(model.columns):
        print(f"Column {i+1}: {col.heading} -> {col.align}")
    print()


def example_3_csv_stringio():
    """Example 3: Reading from CSV with StringIO"""
    print("=== Example 3: CSV from StringIO ===")
    
    csv_data = """Name,Department,Salary
Alice,Engineering,75000
Bob,Marketing,65000
Charlie,Sales,70000"""
    
    stream = io.StringIO(csv_data)
    model = Model.from_csv(stream, headers=True)
    print(Table(model))
    print()


def example_4_columns_mode():
    """Example 4: Column-wise data input"""
    print("=== Example 4: Columns Mode ===")
    
    # Each list represents one column with first element as header
    columns = [
        ["Names", "Alice", "Bob", "Charlie"],
        ["Ages", "25", "30", "35"],
        ["Cities", "NYC", "SF", "Chicago"]
    ]
    
    # Extract headers and data
    headings = [col[0] for col in columns]
    data = [col[1:] for col in columns]
    
    model = Model.from_columns(data, headings=headings)
    print("Column-wise with headers:")
    print(Table(model))
    print()


def example_5_with_aligns_override():
    """Example 5: Override alignments with with_aligns"""
    print("=== Example 5: Alignment Override ===")
    
    data = [
        ["Item", "Price", "Description"],
        ["Apple", "1.25", "Fresh red apples"],
        ["Banana", "0.75", "Ripe yellow bananas"],
        ["Orange", "1.50", "Sweet navel oranges"]
    ]
    
    model = Model.from_rows(data, headers=True)
    print("Default alignment:")
    print(Table(model))
    print()
    
    # Override with specific alignments
    aligned_model = model.with_aligns([Alignment.CENTER, Alignment.RIGHT, Alignment.LEFT])
    print("Custom alignment (center, right, left):")
    print(Table(aligned_model))
    print()


def example_6_mixed_column_objects():
    """Example 6: Using Column objects directly"""
    print("=== Example 6: Mixed Column Objects ===")
    
    # Create some columns directly
    names_col = Column(
        data=["Alice", "Bob", "Charlie"],
        heading="Full Name",
        align=Alignment.LEFT
    )
    
    scores_col = Column(
        data=["95", "87", "92"],
        heading="Score",
        align=Alignment.RIGHT,
        width=8  # Fixed width
    )
    
    # Mix with plain sequence
    grades = ["A", "B", "A-"]
    
    model = Model([names_col, scores_col, grades], headings=["Full Name", "Score", "Grade"])
    print("Mixed Column objects:")
    print(Table(model))
    print()


def example_7_custom_widths_spacer():
    """Example 7: Custom widths and spacer"""
    print("=== Example 7: Custom Spacer ===")
    
    data = [
        ["ID", "Name", "Status"],
        ["1", "Alice", "Active"],
        ["22", "Bob", "Inactive"],
        ["333", "Charlie", "Pending"]
    ]
    
    model = Model.from_rows(data, headers=True)
    
    # Custom spacer
    table = Table(model, spacer=" | ")
    print("With pipe separator:")
    print(table)
    print()


def example_8_table_without_separator():
    """Example 8: Table without separator line"""
    print("=== Example 8: No Separator Line ===")
    
    data = [
        ["Country", "Capital", "Population"],
        ["USA", "Washington DC", "331M"],
        ["UK", "London", "67M"],
        ["France", "Paris", "68M"]
    ]
    
    model = Model.from_rows(data, headers=True)
    
    table = Table(model, show_sep=False)
    print("Table without separator:")
    print(table)
    print()


def example_9_alignment_for_items():
    """Example 9: Alignment.for_items demonstration"""
    print("=== Example 9: Alignment Detection ===")
    
    test_data = [
        (["apple", "banana", "cherry"], "text items"),
        (["123", "456", "789"], "numeric items"),
        (["abc", "def", "ghi"], "same length items"),
        (["1.5", "2.7", "3.9"], "float items"),
        (["A", "BB", "CCC"], "mixed length items")
    ]
    
    for items, description in test_data:
        alignment = Alignment.for_items(items)
        print(f"{description:20} -> {alignment}")
    print()


def example_10_screen_demo():
    """Example 10: Screen vs Table rendering"""
    print("=== Example 10: Screen vs Table ===")
    
    data = [
        ["Tool", "Version"],
        ["Python", "3.12"],
        ["SimpleCOL", "0.1-dev"]
    ]
    
    model = Model.from_rows(data, headers=True)
    
    print("Screen rendering (no headers):")
    print(Screen(model))
    print()
    
    print("Table rendering (with headers):")
    print(Table(model))
    print()


def main():
    """Run all examples"""
    print("SimpleCOL Examples\n" + "=" * 50)
    
    examples = [
        example_1_from_rows,
        example_2_auto_alignment,
        example_3_csv_stringio,
        example_4_columns_mode,
        example_5_with_aligns_override,
        example_6_mixed_column_objects,
        example_7_custom_widths_spacer,
        example_8_table_without_separator,
        example_9_alignment_for_items,
        example_10_screen_demo
    ]
    
    for i, example_func in enumerate(examples, 1):
        try:
            example_func()
            if i < len(examples):
                print()
        except Exception as e:
            print(f"Error in example {i}: {e}")


if __name__ == "__main__":
    main()