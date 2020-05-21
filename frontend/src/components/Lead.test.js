import { shallowMount, createLocalVue } from '@vue/test-utils';
import { BootstrapVue, IconsPlugin } from 'bootstrap-vue';
import Lead from './Lead.vue';
import data from '../../test/test-lead.json';

const localVue = createLocalVue();
localVue.use(BootstrapVue);
localVue.use(IconsPlugin);

describe('Lead', () => {
    it('matches the snapshot', () => {
        const wrapper = shallowMount(Lead, { localVue, propsData: data });
        expect(wrapper).toMatchSnapshot();
    });
});