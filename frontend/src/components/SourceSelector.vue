<template>
  <div class="row">
    <div class="col-sm-4">
      <b-form-checkbox
        ref="fed_check"
        :checked="form.federal.check"
        @input="triggerUpdate('federal', 'check', $event)"
      >Federal</b-form-checkbox>
      <b-form-select
        ref="fed_value"
        @input="triggerUpdate('federal', 'select', $event)"
        :disabled="!form.federal.check"
        :value="form.federal.select"
        :options="federal_options"
      ></b-form-select>
    </div>
    <div class="col-sm-4">
      <b-form-checkbox
        ref="reg_check"
        :checked="form.regional.check"
        @input="triggerUpdate('regional', 'check', $event)"
      >State / Regional</b-form-checkbox>
      <b-form-select
        ref="reg_value"
        @input="triggerUpdate('regional', 'select', $event)"
        :disabled="!form.regional.check"
        :value="form.regional.select"
        :options="regional_options"
      ></b-form-select>
    </div>
    <div class="col-sm-4">
      <b-form-checkbox
        ref="local_check"
        @input="triggerUpdate('local', 'check', $event)"
        :checked="form.local.check"
      >Local</b-form-checkbox>
      <b-form-select
        ref="local_value"
        @input="triggerUpdate('local', 'select', $event)"
        :disabled="!form.local.check"
        :value="form.local.select"
        :options="local_options"
      ></b-form-select>
    </div>
  </div>
</template>

<script>
import { federal_options, regional_options, local_options } from "../constants";

export default {
  name: "SourceSelector",
  props: ["sources"],
  model: { prop: "sources" },
  methods: {
    decodeSourceValue(value) {
      if (value === "exclude") {
        return {
          check: false,
          select: null
        };
      } else if (value === undefined) {
        return {
          check: true,
          select: null
        };
      } else {
        return {
          check: true,
          select: value
        };
      }
    },
    encodeSourceValue({ check, select }) {
      if (!check) {
        return "exclude";
      }
      return select ? select : undefined;
    },
    encode({ federal, regional, local }) {
      return {
        federal: this.encodeSourceValue(federal),
        regional: this.encodeSourceValue(regional),
        local: this.encodeSourceValue(local)
      };
    },
    triggerUpdate(group, key, value) {
      const decoded = Object.assign({}, this.form);
      decoded[group][key] = value;
      this.$emit("input", this.encode(decoded));
    }
  },
  computed: {
    federal_options: () => federal_options,
    regional_options: () => regional_options,
    local_options: () => local_options,
    form() {
      return {
        federal: this.decodeSourceValue(this.sources.federal),
        regional: this.decodeSourceValue(this.sources.regional),
        local: this.decodeSourceValue(this.sources.local)
      };
    }
  }
};
</script>