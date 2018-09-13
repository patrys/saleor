import gql from "graphql-tag";

import {
  OrderCancelMutation,
  OrderCancelMutationVariables,
  OrderCaptureMutation,
  OrderCaptureMutationVariables,
  OrderCreateFulfillmentMutation,
  OrderCreateFulfillmentMutationVariables,
  OrderRefundMutation,
  OrderRefundMutationVariables,
  OrderReleaseMutation,
  OrderReleaseMutationVariables
} from "../gql-types";
import { TypedMutation } from "../mutations";
import { fragmentOrderDetails } from "./queries";

const orderCancelMutation = gql`
  ${fragmentOrderDetails}
  mutation OrderCancel($id: ID!) {
    orderCancel(id: $id, restock: true) {
      order {
        ...OrderDetails
      }
    }
  }
`;
export const TypedOrderCancelMutation = TypedMutation<
  OrderCancelMutation,
  OrderCancelMutationVariables
>(orderCancelMutation);

const orderRefundMutation = gql`
  ${fragmentOrderDetails}
  mutation OrderRefund($id: ID!, $amount: Decimal!) {
    orderRefund(id: $id, amount: $amount) {
      errors {
        field
        message
      }
      order {
        ...OrderDetails
      }
    }
  }
`;
export const TypedOrderRefundMutation = TypedMutation<
  OrderRefundMutation,
  OrderRefundMutationVariables
>(orderRefundMutation);

const orderReleaseMutation = gql`
  ${fragmentOrderDetails}
  mutation OrderRelease($id: ID!) {
    orderRelease(id: $id) {
      order {
        ...OrderDetails
      }
    }
  }
`;
export const TypedOrderReleaseMutation = TypedMutation<
  OrderReleaseMutation,
  OrderReleaseMutationVariables
>(orderReleaseMutation);

const orderCaptureMutation = gql`
  ${fragmentOrderDetails}
  mutation OrderCapture($id: ID!, $amount: Decimal!) {
    orderCapture(id: $id, amount: $amount) {
      errors {
        field
        message
      }
      order {
        ...OrderDetails
      }
    }
  }
`;
export const TypedOrderCaptureMutation = TypedMutation<
  OrderCaptureMutation,
  OrderCaptureMutationVariables
>(orderCaptureMutation);

const orderCreateFulfillmentMutation = gql`
  mutation OrderCreateFulfillment($input: FulfillmentCreateInput!) {
    fulfillmentCreate(input: $input) {
      errors {
        field
        message
      }
      # order {
      #   ...OrderDetails
      # }
    }
  }
`;
export const TypedOrderCreateFulfillmentMutation = TypedMutation<
  OrderCreateFulfillmentMutation,
  OrderCreateFulfillmentMutationVariables
>(orderCreateFulfillmentMutation);
