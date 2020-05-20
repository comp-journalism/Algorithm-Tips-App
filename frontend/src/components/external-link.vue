<template functional>
  <a v-bind="props" target="_blank" rel="noreferrer noopener">
    <slot></slot>
  </a>
</template>

<script>
export default {
  name: "external-link"
};
</script>