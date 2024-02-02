from flask import Flask, render_template, request, redirect, url_for, jsonify

app = Flask(__name__)

# In-memory database to store original memory_blocks
original_blocks = [
    {'size': 100, 'allocated': False},
    {'size': 200, 'allocated': False},
    {'size': 50, 'allocated': False},
    {'size': 300, 'allocated': False}
]

# In-memory database to store dynamic memory_blocks (blocks created during splits)
database = {'memory_blocks': {}}

# Initialize the database with a copy of the original memory blocks for each algorithm
algorithms = ['first_fit', 'best_fit', 'worst_fit', 'last_fit']
for algorithm in algorithms:
    database['memory_blocks'][algorithm] = [{'size': block['size'], 'allocated': block['allocated']} for block in original_blocks]

# Checkpoints list
x = []
sum_blocks = 0
for i in range(len(original_blocks)):
    sum_blocks += original_blocks[i]['size']
    x.append(sum_blocks)

# Sum of all blocks
y = sum_blocks

@app.route('/')
def index():
    num_blocks= len(original_blocks)
    return render_template('index.html', num_blocks=num_blocks, 
                           memory_blocks_first_fit=database['memory_blocks']['first_fit'],
                           memory_blocks_best_fit=database['memory_blocks']['best_fit'],
                           memory_blocks_worst_fit=database['memory_blocks']['worst_fit'],
                           memory_blocks_last_fit=database['memory_blocks']['last_fit'])

@app.route('/set_memory_blocks', methods=['POST'])
def set_memory_blocks():
    num_blocks = int(request.form['num_blocks'])
    block_sizes_input = request.form['block_sizes']

    # Parse comma-separated input into a list of integers
    block_sizes = [int(size.strip()) for size in block_sizes_input.split(',')]

    # Reinitialize memory blocks with user-defined configuration
    for algorithm in algorithms:
        database['memory_blocks'][algorithm] = [{'size': size, 'allocated': False} for size in block_sizes]

    return render_template('index.html', num_blocks=num_blocks,
                           memory_blocks_first_fit=database['memory_blocks']['first_fit'],
                           memory_blocks_best_fit=database['memory_blocks']['best_fit'],
                           memory_blocks_worst_fit=database['memory_blocks']['worst_fit'],
                           memory_blocks_last_fit=database['memory_blocks']['last_fit'])



@app.route('/allocate', methods=['POST'])
def allocate():
    block_size = int(request.form['block_size'])

    # Allocate using each algorithm for the corresponding category
    allocate_first_fit('first_fit', block_size)
    allocate_best_fit('best_fit', block_size)
    allocate_worst_fit('worst_fit', block_size)
    allocate_last_fit('last_fit', block_size)

    return redirect(url_for('index'))

@app.route('/allocate_first_fit', methods=['POST'])
def allocate_first_fit_api():
    block_size = int(request.form['block_size'])
    allocate_first_fit('first_fit', block_size)
    return jsonify(success=True)

@app.route('/allocate_best_fit', methods=['POST'])
def allocate_best_fit_api():
    block_size = int(request.form['block_size'])
    allocate_best_fit('best_fit', block_size)
    return jsonify(success=True)

@app.route('/allocate_worst_fit', methods=['POST'])
def allocate_worst_fit_api():
    block_size = int(request.form['block_size'])
    allocate_worst_fit('worst_fit', block_size)
    return jsonify(success=True)

@app.route('/allocate_last_fit', methods=['POST'])
def allocate_last_fit_api():
    block_size = int(request.form['block_size'])
    allocate_last_fit('last_fit', block_size)
    return jsonify(success=True)


# Update the function signatures for each allocate function
def allocate_first_fit(algorithm, block_size):
    allocate_block(algorithm, block_size)

def allocate_best_fit(algorithm, block_size):
    allocate_block(algorithm, block_size)

def allocate_worst_fit(algorithm, block_size):
    allocate_block(algorithm, block_size)

def allocate_last_fit(algorithm, block_size):
    allocate_block(algorithm, block_size)

def allocate_block(algorithm, block_size):
    if algorithm == 'first_fit':
        allocate_first_fit_block(algorithm, block_size)
    elif algorithm == 'best_fit':
        allocate_best_fit_block(algorithm, block_size)
    elif algorithm == 'worst_fit':
        allocate_worst_fit_block(algorithm, block_size)
    elif algorithm == 'last_fit':
        allocate_last_fit_block(algorithm, block_size)


def allocate_first_fit_block(algorithm, block_size):
    for i, block in enumerate(database['memory_blocks'][algorithm]):
        if not block['allocated'] and block['size'] >= block_size:
            # Split the block if there is extra space
            if block['size'] > block_size:
                split_block(algorithm, i, block_size)
            else:
                database['memory_blocks'][algorithm][i]['allocated'] = True
            break


def allocate_best_fit_block(algorithm, block_size):
    best_fit_index = -1
    best_fit_difference = float('inf')

    for i, block in enumerate(database['memory_blocks'][algorithm]):
        if not block['allocated'] and block['size'] >= block_size:
            difference = block['size'] - block_size

            if difference < best_fit_difference:
                best_fit_index = i
                best_fit_difference = difference
    if best_fit_index != -1:
        # Split the block if there is extra space
        if database['memory_blocks'][algorithm][best_fit_index]['size'] > block_size:
            split_block(algorithm, best_fit_index, block_size)
        else:
            database['memory_blocks'][algorithm][best_fit_index]['allocated'] = True


def allocate_worst_fit_block(algorithm, block_size):
    worst_fit_index = -1
    worst_fit_difference = -1

    for i, block in enumerate(database['memory_blocks'][algorithm]):
        if not block['allocated'] and block['size'] >= block_size:
            difference = block['size'] - block_size

            if difference > worst_fit_difference:
                worst_fit_index = i
                worst_fit_difference = difference

    if worst_fit_index != -1:
        # Split the block if there is extra space
        if database['memory_blocks'][algorithm][worst_fit_index]['size'] > block_size:
            split_block(algorithm, worst_fit_index, block_size)
        else:
            database['memory_blocks'][algorithm][worst_fit_index]['allocated'] = True


def allocate_last_fit_block(algorithm, block_size):
    last_fit_index = -1

    for i, block in enumerate(reversed(database['memory_blocks'][algorithm])):
        if not block['allocated'] and block['size'] >= block_size:
            last_fit_index = len(database['memory_blocks'][algorithm]) - 1 - i
            break

    if last_fit_index != -1:
        # Split the block if there is extra space
        if database['memory_blocks'][algorithm][last_fit_index]['size'] > block_size:
            split_block(algorithm, last_fit_index, block_size)
        else:
            database['memory_blocks'][algorithm][last_fit_index]['allocated'] = True



@app.route('/free_all')
def free_all():
    # Reinitialize memory blocks with the original configuration
    for algorithm in algorithms:
        database['memory_blocks'][algorithm] = [{'size': block['size'], 'allocated': False} for block in original_blocks]

    return jsonify(success=True)


def split_block(algorithm, index, block_size):
    original_size = database['memory_blocks'][algorithm][index]['size']
    remaining_size = original_size - block_size

    # Allocate the requested size
    database['memory_blocks'][algorithm][index]['allocated'] = True
    database['memory_blocks'][algorithm][index]['size'] = block_size

    # Insert a new block for the remaining size
    if remaining_size > 0:
        new_block = {'size': remaining_size, 'allocated': False}
        database['memory_blocks'][algorithm].insert(index + 1, new_block)


def merge_free_blocks(algorithm):
    i = 0
    while i < len(database['memory_blocks'][algorithm]) - 1:
        current_block = database['memory_blocks'][algorithm][i]
        next_block = database['memory_blocks'][algorithm][i + 1]

        if not current_block['allocated'] and not next_block['allocated']:
            # Check if the current or next block is at a checkpoint
            if current_block['size'] in x or next_block['size'] in x:
                i += 1  # Skip merging across checkpoints
            else:
                # Merge adjacent free blocks
                current_block['size'] += next_block['size']
                del database['memory_blocks'][algorithm][i + 1]
        else:
            i += 1

if __name__ == '__main__':
    app.run(debug=True)
