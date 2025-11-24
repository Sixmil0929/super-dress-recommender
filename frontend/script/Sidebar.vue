<template>
  <aside class="sidebar-container">
    <h2>👗 筛选条件</h2>
    <div class="filter-group">
      <h3>季节</h3>
      <ul>
        <li>春季</li>
        <li>夏季</li>
        <li>秋季</li>
        <li>冬季</li>
      </ul>
    </div>
    <div class="filter-group">
      <h3>风格</h3>
      <ul>
        <li>休闲</li>
        <li>商务</li>
        <li>运动</li>
        <li>复古</li>
      </ul>
    </div>
  </aside>
</template>

<style scoped>
.sidebar-container {
  padding: 20px;
  background-color: #ffffff;
  border-right: 1px solid #e0e0e0;
  min-width: 250px;
}

h2 {
  border-bottom: 2px solid #007bff;
  padding-bottom: 10px;
  margin-bottom: 20px;
  color: #007bff;
}

.filter-group {
  margin-bottom: 25px;
}

.filter-group h3 {
  font-size: 1.1em;
  color: #555;
  margin-bottom: 10px;
}

.filter-group ul {
  list-style: none;
  padding: 0;
  margin: 0;
}

.filter-group li {
  padding: 5px 0;
  cursor: pointer;
  color: #666;
}

.filter-group li:hover {
  color: #007bff;
  text-decoration: underline;
}
</style>