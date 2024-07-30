/** @odoo-module **/

import { registry } from '@web/core/registry';
import { MonetaryField } from '@web/views/fields/monetary/monetary_field';
import { getCurrency } from '@web/core/currency';

export class RoundedMonetaryField extends MonetaryField {
    get formattedValue() {
        if (this.props.inputType === 'number' && !this.props.readonly && this.value) {
            return this.value;
        }

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
        }).format(Math.round(this.value));

        const currency = getCurrency(this.currencyId);
        return currency ? `${currency.symbol} ${formattedNumber}` : formattedNumber;
    }

    get currencyId() {
        const currencyField =
            this.props.currencyField ||
            this.props.record.fields[this.props.name].currency_field ||
            'currency_id';
        const currency = this.props.record.data[currencyField];
        return currency && currency[0];
    }
}

registry.category('fields').add('rounded_monetary', {
    component: RoundedMonetaryField,
    supportedTypes: ['monetary', 'float'],
    displayName: 'Rounded Monetary',
});
