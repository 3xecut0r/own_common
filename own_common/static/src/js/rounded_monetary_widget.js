/** @odoo-module **/

import { registry } from '@web/core/registry';
import { MonetaryField } from '@web/views/fields/monetary/monetary_field';

export class RoundedMonetaryField extends MonetaryField {
    get formattedValue() {
        if (this.value == null) {
            return '';
        }

        if (this.props.inputType === 'number' && !this.props.readonly) {
            return this.value;
        }

        const roundedValue = Math.round(this.value);

        let locale = 'en-US';
        try {
            locale = this.props.record.context.lang || 'en-US';
            new Intl.NumberFormat(locale);
        } catch (e) {
            console.warn(`Invalid locale '${locale}' provided, defaulting to 'en-US'.`);
            locale = 'en-US';
        }

        const formattedNumber = new Intl.NumberFormat(locale, {
            minimumFractionDigits: 0,
            maximumFractionDigits: 0,
        }).format(roundedValue);

        const currencySymbol = '$';
        return `${currencySymbol} ${formattedNumber}`;
    }

    get currencyId() {
        const currencyField =
            this.props.currencyField ||
            (this.props.record.fields[this.props.name] ? this.props.record.fields[this.props.name].currency_field : null) ||
            'currency_id';
        const currency = this.props.record.data[currencyField];
        return currency ? currency[0] : null;
    }
}

registry.category('fields').add('rounded_monetary', {
    component: RoundedMonetaryField,
    supportedTypes: ['monetary', 'float'],
    displayName: 'Rounded Monetary',
});
