# SimpleCOL

Easy-to-use columnizer for your shell. Format 2D data into aligned columns with headers support.

## Installation

```bash
pip install simplecol
```

## Usage

### Command Line Interface

SimpleCOL provides a command-line tool for formatting CSV and text data:

```bash
# Basic CSV formatting
echo "Name,Age,City\nAlice,25,New York\nBob,30,San Francisco" | python cli.py

# With headers and separator
echo "Name,Age,City\nAlice,25,New York\nBob,30,San Francisco" | python cli.py --header

# Without separator line  
echo "Name,Age,City\nAlice,25,New York\nBob,30,San Francisco" | python cli.py --header --no-sep

# Custom delimiter and spacer
echo "Name|Age|City\nAlice|25|New York" | python cli.py -d "|" -s " :: "

# Column-wise input (each line defines one column)
echo "Names,Alice,Bob\nAges,25,30" | python cli.py --columns --header

# Auto-detect alignment
echo "Name,Sales\nAlice,1250\nBob,875" | python cli.py --align auto

# Mixed alignment per column
echo "Name,Sales,Notes\nAlice,1250,Excellent\nBob,875,Good" | python cli.py --align "left,right,center"
```

### Python API

```python
from simplecol import Model, Table, Screen, Alignment

# Create from CSV data with headers
import io
csv_data = "Name,Age,City\nAlice,25,New York\nBob,30,San Francisco"
model = Model.from_csv(io.StringIO(csv_data), headers=True)

# Render as table with headers
table = Table(model)
print(table)
# Output:
# Name   Age  City         
# -----  ---  -------------
# Alice   25  New York     
# Bob     30  San Francisco

# Create from row data
rows = [
    ["Product", "Price", "Stock"],
    ["Widget", "12.99", "150"],
    ["Gadget", "25.50", "75"]
]
model = Model.from_rows(rows, headers=True)

# Custom alignment per column
model = model.with_aligns([Alignment.LEFT, Alignment.RIGHT, Alignment.CENTER])
print(Table(model))

# Auto-detect alignment
data = [["apple", "banana"], ["123", "456"]]
model = Model.from_columns(data, align=None)  # None means auto-detect
print(Screen(model))
```

## API Reference

### Core Classes

- **`Alignment`**: Enum with LEFT, RIGHT, CENTER values. Use `Alignment.for_items(data)` for auto-detection.
- **`Column`**: Represents a single column with data, optional heading, width, and alignment.
- **`Model`**: Contains multiple columns with methods for creating from various data sources.
- **`Screen`**: Renders model as plain formatted text.
- **`Table`**: Extends Screen to add header row and optional separator line.

### Model Creation Methods

- `Model.from_rows(rows, headers=False, align=None)`: Create from row-wise data
- `Model.from_csv(stream, delimiter=",", headers=False, align=None)`: Create from CSV stream
- `Model.from_columns(columns, headings=None, align=None)`: Create from column-wise data
- `Model.from_stream(stream, headers=False, align=None)`: Create from text stream

### CLI Options

- `--header`: Treat first row/column as headers
- `--no-sep`: Don't show separator line below headers
- `--columns`: Treat input as column definitions (each line = one column)
- `--align ALIGN`: Set alignment (left/right/center/auto, or comma-separated per column)
- `--delimiter DELIM`: Set field delimiter (default: comma)
- `--spacer SPACER`: Set column separator (default: two spaces)
- `--demo`: Show built-in demonstration

## Examples

See `examples.py` for comprehensive usage examples demonstrating all features.

## License

MIT License - see LICENSE file for details.
