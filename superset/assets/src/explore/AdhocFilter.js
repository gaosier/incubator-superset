import { MULTI_OPERATORS } from './constants';

export const EXPRESSION_TYPES = {
  SIMPLE: 'SIMPLE',
  SQL: 'SQL',
};

export const CLAUSES = {
  HAVING: 'HAVING',
  WHERE: 'WHERE',
};

const OPERATORS_TO_SQL = {
  '==': '=',
  '!=': '<>',
  '>': '>',
  '<': '<',
  '>=': '>=',
  '<=': '<=',
  in: 'in',
  'not in': 'not in',
  LIKE: 'like',
};

const OPERATORS_TO_ZH = {
'==': '等于',
'!=': '不等于',
LIKE: 'like',
'>': '大于',
'>=': '大于等于',
'<': '小于',
'<=': '小于等于',
in: '在',
'not in': '不再',
};

function translateToSql(adhocMetric, { useSimple } = {}) {
  if (adhocMetric.expressionType === EXPRESSION_TYPES.SIMPLE || useSimple) {
    const isMulti = MULTI_OPERATORS.indexOf(adhocMetric.operator) >= 0;
    const operator = OPERATORS_TO_ZH[adhocMetric.operator];
    const comparator = isMulti ? adhocMetric.comparator.join("','") : adhocMetric.comparator;
    const verbose_name = adhocMetric.verbose_name;
    return `${verbose_name} ${operator} ${isMulti ? '(\'' : ''}${comparator}${isMulti ? '\')' : ''}`;
  } else if (adhocMetric.expressionType === EXPRESSION_TYPES.SQL) {
    return adhocMetric.sqlExpression;
  }
  return '';
}

export default class AdhocFilter {
  constructor(adhocFilter) {
    this.expressionType = adhocFilter.expressionType || EXPRESSION_TYPES.SIMPLE;
    if (this.expressionType === EXPRESSION_TYPES.SIMPLE) {
      this.subject = adhocFilter.subject;
      this.operator = adhocFilter.operator;
      this.comparator = adhocFilter.comparator;
      this.clause = adhocFilter.clause;
      this.sqlExpression = null;
      this.verbose_name = adhocFilter.verbose_name;
    } else if (this.expressionType === EXPRESSION_TYPES.SQL) {
      this.sqlExpression = typeof adhocFilter.sqlExpression === 'string' ?
        adhocFilter.sqlExpression :
        translateToSql(adhocFilter, { useSimple: true });
      this.clause = adhocFilter.clause;
      this.subject = null;
      this.operator = null;
      this.comparator = null;
      this.verbose_name = null;
    }
    this.fromFormData = !!adhocFilter.filterOptionName;

    this.filterOptionName = adhocFilter.filterOptionName ||
      `filter_${Math.random().toString(36).substring(2, 15)}_${Math.random().toString(36).substring(2, 15)}`;
  }

  duplicateWith(nextFields) {
    return new AdhocFilter({
      ...this,
      expressionType: this.expressionType,
      subject: this.subject,
      operator: this.operator,
      clause: this.clause,
      sqlExpression: this.sqlExpression,
      fromFormData: this.fromFormData,
      filterOptionName: this.filterOptionName,
      verbose_name: this.verbose_name,
      ...nextFields,
    });
  }

  equals(adhocFilter) {
    return adhocFilter.expressionType === this.expressionType &&
      adhocFilter.sqlExpression === this.sqlExpression &&
      adhocFilter.operator === this.operator &&
      adhocFilter.comparator === this.comparator &&
      adhocFilter.subject === this.subject &&
      adhocFilter.verbose_name === this.verbose_name;
  }

  isValid() {
    if (this.expressionType === EXPRESSION_TYPES.SIMPLE) {
      if (typeof (this.comparator) === 'number' && this.comparator === 0) {
        return !!(
        this.operator &&
        this.subject &&
        this.clause
      );
      }

      let comparator_length = typeof (this.comparator) === 'number' ? this.comparator.toString().length : this.comparator.length;
      return !!(
      this.operator &&
      this.subject &&
      this.comparator &&
      comparator_length &&
      this.clause
      );

    } else if (this.expressionType === EXPRESSION_TYPES.SQL) {
      return !!(this.sqlExpression && this.clause);
    }
    return false;
  }

  getDefaultLabel() {
    const label = this.translateToSql();
    return label.length < 43 ?
      label :
      label.substring(0, 40) + '...';
  }

  translateToSql() {
    return translateToSql(this);
  }
}
