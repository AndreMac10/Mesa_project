
<template>
  <svg
    :width="canvas_size"
    :height="canvas_size"
    style="display:block; cursor:pointer;"
    @click.native="handleClick"
  >
    <rect
      v-for="cell in cells"
      :key="cell.key"
      :x="cell.x"
      :y="cell.y"
      :width="cell_size"
      :height="cell_size"
      :fill="cell.color"
      stroke="none"
    />
  </svg>
</template>

<script>
module.exports = {
  props: {
    cells:       { type: Array,  default: () => [] },
    grid_size:   { type: Number, default: 30 },
    canvas_size: { type: Number, default: 700 },
  },
  computed: {
    cell_size() {
      return this.canvas_size / this.grid_size;
    }
  },
  methods: {
    handleClick(event) {
      const rect = event.currentTarget.getBoundingClientRect();
      const px   = event.clientX - rect.left;
      const py   = event.clientY - rect.top;
      const col  = Math.floor(px / this.cell_size);
      const row  = Math.floor(py / this.cell_size);
      // row 0 in SVG = top, but Mesa grid row 0 = bottom → flip
      const mesa_row = this.grid_size - 1 - row;
      this.$emit("cell_clicked", { col: col, row: mesa_row });
    }
  }
};
</script>
