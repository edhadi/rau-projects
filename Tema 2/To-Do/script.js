let tasks = JSON.parse(localStorage.getItem('tasks')) || [];

function addTask() {
    let taskInput = document.getElementById('taskInput');
    let task = { text: taskInput.value, completed: false };
    tasks.push(task);
    localStorage.setItem('tasks', JSON.stringify(tasks));
    taskInput.value = '';
    loadTasks();
}

function deleteTask(index) {
    tasks.splice(index, 1);
    localStorage.setItem('tasks', JSON.stringify(tasks));
    loadTasks();
}

function toggleTask(index) {
    tasks[index].completed = !tasks[index].completed;
    localStorage.setItem('tasks', JSON.stringify(tasks));
    loadTasks();
}

function editTask(index) {
    let newTask = prompt('Edit task', tasks[index].text);
    if (newTask) {
        tasks[index].text = newTask;
        localStorage.setItem('tasks', JSON.stringify(tasks));
        loadTasks();
    }
}

function loadTasks() {
    let taskList = document.getElementById('taskList');
    taskList.innerHTML = '';
    tasks.forEach((task, index) => {
        let taskElement = document.createElement('div');
        taskElement.innerHTML = `
            <span class="${task.completed ? 'completed' : ''}" onclick="toggleTask(${index})">${task.text}</span>
            <button onclick="editTask(${index})">Edit</button>
            <button onclick="deleteTask(${index})">Delete</button>
        `;
        taskList.appendChild(taskElement);
    });
}

loadTasks();